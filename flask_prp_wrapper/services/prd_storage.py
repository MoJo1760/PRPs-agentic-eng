"""PRD document storage service for managing uploaded documents."""

import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from ..models.prd_document import (
    PRDDocument,
    PRDSection,
    PRDContentExtraction,
    PRDProcessingMetrics,
)

logger = logging.getLogger(__name__)


class PRDStorageService:
    """Service for managing PRD document storage and retrieval."""

    def __init__(
        self, storage_path: Optional[str] = None, cache_max_size: Optional[int] = None
    ):
        """Initialize PRD storage service.

        Args:
            storage_path: Base path for PRD document storage
            cache_max_size: Maximum number of documents to cache
        """
        from flask import current_app

        # Get configuration from Flask app if available, otherwise use defaults
        try:
            config = current_app.config
            default_storage_path = config.get(
                "PRD_STORAGE_PATH", "/tmp/flask_prp/prd_documents"
            )
            default_cache_size = config.get("PRD_CACHE_MAX_SIZE", 100)
        except RuntimeError:
            # Not in app context, use defaults
            default_storage_path = "/tmp/flask_prp/prd_documents"
            default_cache_size = 100

        self.storage_path = Path(storage_path or default_storage_path)
        self.documents_path = self.storage_path / "documents"
        self.metadata_path = self.storage_path / "metadata"

        # Ensure directories exist
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache for recently accessed documents
        self._document_cache: Dict[str, PRDDocument] = {}
        self._cache_max_size = cache_max_size or default_cache_size

    async def store_prd_document(
        self,
        concept_id: str,
        file_content: bytes,
        filename: str,
        parsed_sections: Optional[List[PRDSection]] = None,
        content_extraction: Optional[PRDContentExtraction] = None,
        processing_metrics: Optional[PRDProcessingMetrics] = None,
    ) -> str:
        """Store uploaded PRD document and return document ID.

        Args:
            concept_id: Associated business concept ID
            file_content: Raw file content
            filename: Original filename
            parsed_sections: Parsed PRD sections (optional)
            content_extraction: Extracted business content (optional)
            processing_metrics: Processing metrics (optional)

        Returns:
            Generated document ID
        """
        document_id = self._generate_document_id(concept_id, filename)

        try:
            # Store raw file content
            await self._store_raw_file(document_id, file_content, filename)

            # Create PRD document metadata
            prd_document = PRDDocument(
                document_id=document_id,
                concept_id=concept_id,
                filename=filename,
                file_size_bytes=len(file_content),
                sections=parsed_sections or [],
                processing_status="uploaded",
            )

            # Add extracted content if available
            if content_extraction:
                prd_document.extracted_business_context = content_extraction.dict()

            # Calculate quality scores
            if parsed_sections:
                prd_document.extraction_quality_score = (
                    self._calculate_extraction_quality(parsed_sections)
                )
                prd_document.total_word_count = sum(
                    s.word_count for s in parsed_sections
                )
                prd_document.coverage_areas = self._calculate_coverage_areas(
                    parsed_sections
                )

            # Store metadata
            await self._store_metadata(document_id, prd_document)

            # Update cache
            self._update_cache(document_id, prd_document)

            logger.info(
                f"Successfully stored PRD document {document_id} for concept {concept_id}"
            )
            return document_id

        except Exception as e:
            logger.error(f"Error storing PRD document: {e}")
            # Cleanup partial storage
            await self._cleanup_document(document_id)
            raise

    async def get_prd_document(self, document_id: str) -> Optional[PRDDocument]:
        """Retrieve PRD document by ID.

        Args:
            document_id: Document ID to retrieve

        Returns:
            PRDDocument if found, None otherwise
        """
        # Check cache first
        if document_id in self._document_cache:
            logger.debug(f"Retrieved PRD document {document_id} from cache")
            return self._document_cache[document_id]

        try:
            # Load from storage
            metadata_file = self.metadata_path / f"{document_id}.json"
            if not metadata_file.exists():
                logger.warning(f"PRD document {document_id} not found")
                return None

            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Reconstruct PRDDocument
            prd_document = PRDDocument(**metadata)

            # Update cache
            self._update_cache(document_id, prd_document)

            logger.debug(f"Retrieved PRD document {document_id} from storage")
            return prd_document

        except Exception as e:
            logger.error(f"Error retrieving PRD document {document_id}: {e}")
            return None

    async def list_concept_prds(self, concept_id: str) -> List[PRDDocument]:
        """List all PRD documents associated with a concept.

        Args:
            concept_id: Business concept ID

        Returns:
            List of PRD documents for the concept
        """
        try:
            documents = []

            # Scan metadata files for matching concept_id
            for metadata_file in self.metadata_path.glob("*.json"):
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    if metadata.get("concept_id") == concept_id:
                        prd_document = PRDDocument(**metadata)
                        documents.append(prd_document)

                except Exception as e:
                    logger.warning(f"Error reading metadata file {metadata_file}: {e}")
                    continue

            # Sort by upload timestamp (newest first)
            documents.sort(key=lambda x: x.upload_timestamp, reverse=True)

            logger.debug(
                f"Found {len(documents)} PRD documents for concept {concept_id}"
            )
            return documents

        except Exception as e:
            logger.error(f"Error listing PRD documents for concept {concept_id}: {e}")
            return []

    async def get_raw_file_content(self, document_id: str) -> Optional[bytes]:
        """Get raw file content for a PRD document.

        Args:
            document_id: Document ID

        Returns:
            Raw file content if found, None otherwise
        """
        try:
            # Find document file (could have various extensions)
            for ext in [".md", ".markdown", ".txt"]:
                file_path = self.documents_path / f"{document_id}{ext}"
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        content = f.read()
                    logger.debug(f"Retrieved raw content for document {document_id}")
                    return content

            logger.warning(f"Raw file not found for document {document_id}")
            return None

        except Exception as e:
            logger.error(
                f"Error retrieving raw content for document {document_id}: {e}"
            )
            return None

    async def update_prd_document(
        self, document_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Update PRD document metadata.

        Args:
            document_id: Document ID to update
            updates: Fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current document
            prd_document = await self.get_prd_document(document_id)
            if not prd_document:
                return False

            # Apply updates
            for field, value in updates.items():
                if hasattr(prd_document, field):
                    setattr(prd_document, field, value)

            # Save updated metadata
            await self._store_metadata(document_id, prd_document)

            # Update cache
            self._update_cache(document_id, prd_document)

            logger.info(f"Updated PRD document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating PRD document {document_id}: {e}")
            return False

    async def delete_prd_document(self, document_id: str) -> bool:
        """Delete PRD document and associated data.

        Args:
            document_id: Document ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from cache
            self._document_cache.pop(document_id, None)

            # Delete files
            success = await self._cleanup_document(document_id)

            if success:
                logger.info(f"Successfully deleted PRD document {document_id}")
            else:
                logger.warning(f"Partial deletion of PRD document {document_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting PRD document {document_id}: {e}")
            return False

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics
        """
        try:
            stats: Dict[str, Any] = {
                "total_documents": 0,
                "total_size_bytes": 0,
                "documents_by_status": {},
                "documents_by_concept": {},
                "storage_path": str(self.storage_path),
                "cache_size": len(self._document_cache),
            }

            # Scan all metadata files
            for metadata_file in self.metadata_path.glob("*.json"):
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    stats["total_documents"] += 1
                    stats["total_size_bytes"] += metadata.get("file_size_bytes", 0)

                    # Count by status
                    status = metadata.get("processing_status", "unknown")
                    stats["documents_by_status"][status] = (
                        stats["documents_by_status"].get(status, 0) + 1
                    )

                    # Count by concept
                    concept_id = metadata.get("concept_id", "unknown")
                    stats["documents_by_concept"][concept_id] = (
                        stats["documents_by_concept"].get(concept_id, 0) + 1
                    )

                except Exception as e:
                    logger.warning(f"Error reading metadata file {metadata_file}: {e}")
                    continue

            return stats

        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}

    async def cleanup_old_documents(self, days_old: int = 30) -> int:
        """Clean up documents older than specified days.

        Args:
            days_old: Delete documents older than this many days

        Returns:
            Number of documents cleaned up
        """
        try:
            cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 60 * 60)
            cleaned_count = 0

            for metadata_file in self.metadata_path.glob("*.json"):
                try:
                    file_mtime = metadata_file.stat().st_mtime
                    if file_mtime < cutoff_time:
                        # Get document ID from filename
                        document_id = metadata_file.stem

                        # Delete document
                        if await self.delete_prd_document(document_id):
                            cleaned_count += 1

                except Exception as e:
                    logger.warning(f"Error cleaning up document {metadata_file}: {e}")
                    continue

            logger.info(f"Cleaned up {cleaned_count} old PRD documents")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

    def _generate_document_id(self, concept_id: str, filename: str) -> str:
        """Generate unique document ID."""
        timestamp = str(int(datetime.utcnow().timestamp()))
        content = f"{concept_id}_{filename}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _store_raw_file(
        self, document_id: str, content: bytes, filename: str
    ) -> None:
        """Store raw file content."""
        # Determine file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in [".md", ".markdown", ".txt"]:
            file_ext = ".md"  # Default to markdown

        file_path = self.documents_path / f"{document_id}{file_ext}"

        with open(file_path, "wb") as f:
            f.write(content)

        logger.debug(f"Stored raw file for document {document_id}")

    async def _store_metadata(
        self, document_id: str, prd_document: PRDDocument
    ) -> None:
        """Store document metadata."""
        metadata_file = self.metadata_path / f"{document_id}.json"

        # Convert to dict for JSON serialization
        metadata = prd_document.dict()

        # Handle datetime serialization
        if "upload_timestamp" in metadata:
            metadata["upload_timestamp"] = metadata["upload_timestamp"].isoformat()

        # Handle nested datetime fields in sections
        for section in metadata.get("sections", []):
            # PRDSection doesn't have datetime fields, but keeping for future extensibility
            pass

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.debug(f"Stored metadata for document {document_id}")

    async def _cleanup_document(self, document_id: str) -> bool:
        """Clean up all files for a document."""
        success = True

        try:
            # Remove raw file (try different extensions)
            for ext in [".md", ".markdown", ".txt"]:
                file_path = self.documents_path / f"{document_id}{ext}"
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted raw file {file_path}")

            # Remove metadata file
            metadata_file = self.metadata_path / f"{document_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
                logger.debug(f"Deleted metadata file {metadata_file}")

        except Exception as e:
            logger.error(f"Error during cleanup of document {document_id}: {e}")
            success = False

        return success

    def _update_cache(self, document_id: str, prd_document: PRDDocument) -> None:
        """Update document cache with size limit."""
        # Remove oldest entries if cache is full
        if len(self._document_cache) >= self._cache_max_size:
            # Remove 10% of oldest entries
            remove_count = max(1, self._cache_max_size // 10)
            oldest_keys = list(self._document_cache.keys())[:remove_count]
            for key in oldest_keys:
                del self._document_cache[key]

        # Add/update entry
        self._document_cache[document_id] = prd_document

    def _calculate_extraction_quality(self, sections: List[PRDSection]) -> float:
        """Calculate extraction quality score based on sections."""
        if not sections:
            return 0.0

        # Quality factors
        section_count_factor = min(1.0, len(sections) / 5.0)  # Optimal: 5+ sections

        avg_confidence = sum(s.confidence_score for s in sections) / len(sections)

        total_words = sum(s.word_count for s in sections)
        word_count_factor = min(1.0, total_words / 1000)  # Optimal: 1000+ words

        # Check for key section types
        section_types = {s.section_type for s in sections}
        key_types = {"overview", "requirements", "users", "business_model"}
        coverage_factor = len(section_types & key_types) / len(key_types)

        # Combine factors
        quality_score = (
            section_count_factor * 0.25
            + avg_confidence * 0.35
            + word_count_factor * 0.25
            + coverage_factor * 0.15
        ) * 10.0

        return min(10.0, quality_score)

    def _calculate_coverage_areas(self, sections: List[PRDSection]) -> Dict[str, float]:
        """Calculate coverage by business area."""
        coverage = {
            "overview": 0.0,
            "users": 0.0,
            "requirements": 0.0,
            "technical": 0.0,
            "business_model": 0.0,
            "competitive": 0.0,
            "user_stories": 0.0,
            "metrics": 0.0,
        }

        for section in sections:
            if section.section_type in coverage:
                # Score based on word count and confidence
                score = min(1.0, (section.word_count / 100) * section.confidence_score)
                coverage[section.section_type] = max(
                    coverage[section.section_type], score
                )

        return coverage
