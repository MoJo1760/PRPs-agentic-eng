"""PRD document parsing service for extracting structured content from markdown."""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Literal, cast

from ..models.prd_document import (
    PRDSection,
    PRDContentExtraction,
    PRDValidationResult,
)
from ..models.gap_analysis import KnowledgeGap

logger = logging.getLogger(__name__)


class PRDParserService:
    """Service for parsing and extracting content from PRD documents."""

    def __init__(self):
        """Initialize the PRD parser with section patterns and keywords."""

        # Comprehensive regex patterns for identifying different PRD sections
        # Supports various naming conventions and formats
        self.section_patterns = {
            "overview": [
                r"#\s*(product\s+)?overview",
                r"#\s*(executive\s+)?summary",
                r"#\s*introduction",
                r"#\s*executive\s+summary",
                r"#\s*product\s+(description|vision|summary)",
                r"#\s*vision(\s+and\s+mission)?",
                r"#\s*mission(\s+statement)?",
                r"#\s*project\s+(overview|summary|description)",
                r"#\s*about(\s+this\s+product)?",
                r"#\s*purpose",
                r"#\s*problem\s+(statement|definition)",
                r"#\s*solution\s+(overview|description)",
                r"#\s*background",
                r"#\s*context",
            ],
            "users": [
                r"#\s*target\s+(users?|market|audience|customers?)",
                r"#\s*user\s+(personas?|profiles?|segments?|groups?)",
                r"#\s*customers?(\s+segments?)?",
                r"#\s*market\s+(segment|analysis|research)",
                r"#\s*audience(\s+analysis)?",
                r"#\s*stakeholders?",
                r"#\s*end\s+users?",
                r"#\s*personas?",
                r"#\s*who\s+(will\s+use|uses?)",
                r"#\s*user\s+base",
                r"#\s*demographics",
                r"#\s*target\s+market",
            ],
            "requirements": [
                r"#\s*(functional\s+)?requirements",
                r"#\s*features?(\s+list)?",
                r"#\s*(product\s+)?scope",
                r"#\s*product\s+features",
                r"#\s*functionality",
                r"#\s*capabilities",
                r"#\s*specifications",
                r"#\s*core\s+features",
                r"#\s*key\s+features",
                r"#\s*feature\s+(set|list|requirements)",
                r"#\s*system\s+features",
                r"#\s*must\s+have",
                r"#\s*nice\s+to\s+have",
                r"#\s*acceptance\s+criteria",
                r"#\s*definition\s+of\s+done",
            ],
            "technical": [
                r"#\s*technical\s+(requirements|specifications|constraints|architecture)",
                r"#\s*(system\s+)?architecture",
                r"#\s*implementation(\s+details)?",
                r"#\s*technology\s+(stack|choices|requirements)",
                r"#\s*tech\s+(stack|specifications?|requirements?)",
                r"#\s*system\s+(requirements|design|specs)",
                r"#\s*infrastructure(\s+requirements?)?",
                r"#\s*platform(\s+requirements?)?",
                r"#\s*development\s+(environment|stack|platform)",
                r"#\s*non.functional\s+requirements",
                r"#\s*performance\s+(requirements|specs)",
                r"#\s*security\s+(requirements|considerations)",
                r"#\s*scalability(\s+requirements?)?",
                r"#\s*api\s+(design|specifications)",
                r"#\s*database\s+(design|requirements)",
                r"#\s*deployment(\s+strategy)?",
                r"#\s*hosting(\s+requirements?)?",
                r"#\s*devops",
                r"#\s*ci.cd",
                r"#\s*tools?\s+(and\s+)?technologies?",
            ],
            "business_model": [
                r"#\s*(business\s+)?(model|strategy)",
                r"#\s*(monetization|revenue)\s*(model|strategy)?",
                r"#\s*pricing(\s+strategy|model)?",
                r"#\s*business\s+(case|justification)",
                r"#\s*revenue\s+(model|streams?)",
                r"#\s*go.to.market(\s+strategy)?",
                r"#\s*market\s+(strategy|approach)",
                r"#\s*financial\s+(model|projections)",
                r"#\s*cost\s+(structure|model)",
                r"#\s*value\s+proposition",
                r"#\s*business\s+objectives",
                r"#\s*commercial\s+(model|aspects)",
            ],
            "competitive": [
                r"#\s*competitive?\s+(analysis|landscape|research|intelligence)",
                r"#\s*competitors?(\s+analysis)?",
                r"#\s*market\s+(analysis|research|landscape|competition)",
                r"#\s*competitor\s+(research|analysis|comparison)",
                r"#\s*competitive\s+(positioning|advantage)",
                r"#\s*market\s+positioning",
                r"#\s*alternatives?",
                r"#\s*similar\s+(products|solutions)",
                r"#\s*existing\s+solutions",
                r"#\s*benchmarking",
                r"#\s*swot\s+analysis",
                r"#\s*competition",
                r"#\s*competing\s+(products|solutions)",
                r"#\s*market\s+(landscape|overview)",
            ],
            "user_stories": [
                r"#\s*user\s+(stories|story|scenarios?)",
                r"#\s*use\s+cases",
                r"#\s*scenarios?",
                r"#\s*user\s+journeys?",
                r"#\s*workflows?",
                r"#\s*user\s+(flows?|paths?)",
                r"#\s*epics?",
                r"#\s*story\s+(map|mapping)",
                r"#\s*user\s+interactions?",
                r"#\s*user\s+experience\s+flows?",
            ],
            "metrics": [
                r"#\s*(success\s+)?metrics",
                r"#\s*kpis?",
                r"#\s*(business\s+)?goals",
                r"#\s*objectives",
                r"#\s*success\s+(criteria|factors|measures)",
                r"#\s*performance\s+(indicators|metrics)",
                r"#\s*measurement\s+(plan|strategy)",
                r"#\s*analytics",
                r"#\s*tracking",
                r"#\s*milestones",
                r"#\s*targets?",
                r"#\s*outcomes?",
                r"#\s*results?",
            ],
        }

        # Keywords for extracting business context
        self.business_keywords = {
            "target_users": [
                "users",
                "customers",
                "audience",
                "personas",
                "segments",
                "demographics",
                "market",
                "buyers",
                "consumers",
            ],
            "business_model": [
                "revenue",
                "pricing",
                "subscription",
                "freemium",
                "saas",
                "marketplace",
                "commission",
                "advertising",
                "monetization",
            ],
            "technical": [
                "api",
                "database",
                "server",
                "cloud",
                "security",
                "architecture",
                "framework",
                "technology",
                "platform",
                "integration",
            ],
            "competitive": [
                "competitors",
                "alternative",
                "similar",
                "market leader",
                "competitive advantage",
                "differentiation",
            ],
        }

    async def parse_prd_content(self, content: str, filename: str) -> List[PRDSection]:
        """Parse PRD markdown content into structured sections.

        Args:
            content: Raw markdown content
            filename: Original filename for context

        Returns:
            List of parsed PRD sections
        """
        logger.info(f"Parsing PRD content from {filename}")

        try:
            # Clean and normalize content
            normalized_content = self._normalize_markdown_content(content)

            # Extract sections based on markdown headers
            raw_sections = self._extract_markdown_sections(normalized_content)

            # Process and classify sections
            processed_sections = []
            for raw_section in raw_sections:
                section = await self._process_section(raw_section)
                if section:
                    processed_sections.append(section)

            logger.info(
                f"Successfully parsed {len(processed_sections)} sections from {filename}"
            )
            return processed_sections

        except Exception as e:
            logger.error(f"Error parsing PRD content from {filename}: {e}")
            raise

    async def extract_business_context(
        self, sections: List[PRDSection]
    ) -> PRDContentExtraction:
        """Extract business concept context from PRD sections.

        Args:
            sections: List of parsed PRD sections

        Returns:
            Structured business context extraction
        """
        logger.debug(f"Extracting business context from {len(sections)} sections")

        extraction = PRDContentExtraction()

        for section in sections:
            if section.section_type == "overview":
                extraction.product_overview = self._extract_overview_content(
                    section.content
                )

            elif section.section_type == "users":
                extraction.target_users = self._extract_users_content(section.content)

            elif section.section_type == "business_model":
                extraction.business_model = self._extract_business_model_content(
                    section.content
                )

            elif section.section_type == "technical":
                extraction.technical_requirements = self._extract_technical_content(
                    section.content
                )

            elif section.section_type == "competitive":
                extraction.competitive_analysis = self._extract_competitive_content(
                    section.content
                )

            elif section.section_type == "user_stories":
                user_stories = self._extract_user_stories_list(section.content)
                extraction.user_stories.extend(user_stories)

            elif section.section_type == "metrics":
                metrics = self._extract_metrics_list(section.content)
                extraction.success_metrics.extend(metrics)

            elif section.section_type == "requirements":
                functional, non_functional = self._extract_requirements_lists(
                    section.content
                )
                extraction.functional_requirements.extend(functional)
                extraction.non_functional_requirements.extend(non_functional)

        # Extract additional structured information
        extraction.assumptions = self._extract_assumptions(sections)
        extraction.constraints = self._extract_constraints(sections)
        extraction.risks = self._extract_risks(sections)
        extraction.timeline = self._extract_timeline_info(sections)
        extraction.budget = self._extract_budget_info(sections)

        return extraction

    async def calculate_coverage_improvement(
        self, prd_sections: List[PRDSection], existing_gaps: List[KnowledgeGap]
    ) -> float:
        """Calculate how much PRD content improves gap coverage.

        Args:
            prd_sections: Parsed PRD sections
            existing_gaps: Current knowledge gaps

        Returns:
            Coverage improvement percentage (0-100)
        """
        if not existing_gaps:
            return 0.0

        # Map PRD content to gap categories
        prd_coverage = self._analyze_prd_section_coverage(prd_sections)

        # Calculate improvement for each gap category
        total_improvement = 0.0
        covered_gaps = 0

        for gap in existing_gaps:
            gap_category = gap.category
            if gap_category in prd_coverage:
                coverage_score = prd_coverage[gap_category]
                # Weight by gap priority
                weight = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}.get(
                    gap.priority, 0.6
                )
                total_improvement += coverage_score * weight
                covered_gaps += 1

        if covered_gaps == 0:
            return 0.0

        return min(100.0, (total_improvement / covered_gaps) * 100)

    async def validate_prd_content(
        self, content: str, filename: str
    ) -> PRDValidationResult:
        """Validate PRD content quality and completeness.

        Args:
            content: Raw PRD content
            filename: Filename for context

        Returns:
            Validation result with quality metrics
        """
        result = PRDValidationResult(
            is_valid=True,
            content_quality_score=0.0,
            completeness_score=0.0,
            structure_score=0.0,
            min_sections_found=False,
            estimated_coverage_improvement=0.0,
        )

        # Basic content validation
        if len(content.strip()) < 500:
            result.validation_errors.append(
                "PRD content is too short (minimum 500 characters)"
            )
            result.is_valid = False

        # Check for markdown headers
        header_count = len(re.findall(r"^#+\s+", content, re.MULTILINE))
        if header_count < 3:
            result.validation_warnings.append(
                "PRD has fewer than 3 sections, may lack structure"
            )

        # Check for minimum required sections
        sections = await self.parse_prd_content(content, filename)
        required_section_types = {"overview", "requirements"}
        found_types = {s.section_type for s in sections}

        result.min_sections_found = required_section_types.issubset(found_types)
        if not result.min_sections_found:
            missing = required_section_types - found_types
            result.validation_warnings.append(
                f"Missing recommended sections: {', '.join(missing)}"
            )

        # Calculate quality scores
        result.content_quality_score = self._calculate_content_quality(
            sections, content
        )
        result.completeness_score = len(found_types) / 8.0  # 8 possible section types
        result.structure_score = min(1.0, header_count / 5.0)  # Normalize to 1.0
        result.estimated_coverage_improvement = (
            await self.calculate_coverage_improvement(
                sections,
                [],  # No existing gaps for estimation
            )
        )

        return result

    def _normalize_markdown_content(self, content: str) -> str:
        """Normalize markdown content for consistent parsing."""
        # Remove BOM and normalize line endings
        content = (
            content.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
        )

        # Normalize header spacing
        content = re.sub(r"^(#+)([^\s#])", r"\1 \2", content, flags=re.MULTILINE)

        # Remove excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        return content.strip()

    def _extract_markdown_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections based on markdown headers."""
        sections: List[Dict[str, Any]] = []
        lines = content.split("\n")
        current_section = None

        for line in lines:
            # Check if line is a header
            header_match = re.match(r"^(#+)\s+(.+)$", line.strip())

            if header_match:
                # Save previous section
                if current_section:
                    sections.append(current_section)

                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {"title": title, "level": level, "content_lines": []}
            else:
                # Add content to current section
                if current_section:
                    current_section["content_lines"].append(line)

        # Add final section
        if current_section:
            sections.append(current_section)

        # Process content for each section
        for section in sections:
            section["content"] = "\n".join(section["content_lines"]).strip()
            section["word_count"] = (
                len(section["content"].split()) if section["content"] else 0
            )
            del section["content_lines"]  # Clean up

        return sections

    async def _process_section(
        self, raw_section: Dict[str, Any]
    ) -> Optional[PRDSection]:
        """Process and classify a raw section."""
        title = raw_section["title"]
        content = raw_section["content"]
        level = raw_section["level"]
        word_count = raw_section["word_count"]

        # Skip very short sections
        if word_count < 10:
            return None

        # Classify section type
        section_type_str, confidence = self._classify_section_type(title, content)
        # Ensure section_type is a valid Literal value
        valid_types = {
            "overview",
            "users",
            "requirements",
            "technical",
            "business_model",
            "competitive",
            "user_stories",
            "metrics",
            "other",
        }
        section_type = section_type_str if section_type_str in valid_types else "other"

        # Extract keywords
        keywords = self._extract_keywords_from_content(content)

        return PRDSection(
            title=title,
            content=content,
            section_type=cast(
                Literal[
                    "overview",
                    "users",
                    "requirements",
                    "technical",
                    "business_model",
                    "competitive",
                    "user_stories",
                    "metrics",
                    "other",
                ],
                section_type,
            ),
            confidence_score=confidence,
            extracted_keywords=keywords,
            section_level=level,
            word_count=word_count,
        )

    def _classify_section_type(self, title: str, content: str) -> Tuple[str, float]:
        """Classify section type based on title and content with semantic analysis."""
        title_lower = title.lower()
        content_lower = content.lower()

        best_type = "other"
        best_score = 0.0

        # Enhanced semantic keywords for better content classification
        enhanced_keywords = {
            "overview": [
                "overview", "summary", "introduction", "vision", "mission", "purpose", 
                "problem", "solution", "background", "context", "about", "description",
                "goal", "objective", "product", "platform", "system", "application"
            ],
            "users": [
                "users", "customers", "audience", "personas", "segments", "demographics",
                "market", "buyers", "consumers", "stakeholders", "target", "who", "user",
                "customer", "persona", "segment", "audience", "end user", "stakeholder"
            ],
            "requirements": [
                "requirements", "features", "functionality", "capabilities", "specifications",
                "scope", "must have", "should have", "functional", "feature", "requirement",
                "capability", "specification", "acceptance", "criteria", "definition"
            ],
            "technical": [
                "technical", "architecture", "infrastructure", "technology", "platform",
                "api", "database", "server", "cloud", "security", "performance", "scalability",
                "implementation", "system", "framework", "library", "tool", "service"
            ],
            "business_model": [
                "business", "revenue", "pricing", "monetization", "subscription", "freemium",
                "marketplace", "commission", "advertising", "model", "strategy", "financial",
                "cost", "value", "proposition", "commercial", "sales", "market"
            ],
            "competitive": [
                "competitive", "competitor", "competition", "alternative", "similar",
                "market analysis", "benchmarking", "positioning", "advantage", "comparison",
                "landscape", "existing", "solutions", "alternatives", "swot"
            ],
            "user_stories": [
                "user stories", "use cases", "scenarios", "journeys", "workflows", "flows",
                "interactions", "experience", "story", "epic", "persona", "as a", "i want",
                "so that", "given", "when", "then"
            ],
            "metrics": [
                "metrics", "kpi", "goals", "objectives", "success", "performance", "indicators",
                "measurement", "analytics", "tracking", "milestones", "targets", "outcomes",
                "results", "measure", "monitor", "evaluate"
            ]
        }

        for section_type, patterns in self.section_patterns.items():
            score = 0.0

            # Check title patterns (highest weight)
            for pattern in patterns:
                if re.search(pattern, title_lower, re.IGNORECASE):
                    score = max(score, 0.9)
                    break

            # Enhanced content analysis with semantic keywords
            if score < 0.7:  # Only do content analysis if title didn't match well
                semantic_keywords = enhanced_keywords.get(section_type, [])
                content_matches = sum(
                    1 for keyword in semantic_keywords 
                    if keyword.lower() in content_lower
                )
                
                if semantic_keywords:
                    # Improved scoring based on keyword density and variety
                    keyword_density = content_matches / len(semantic_keywords)
                    content_length_factor = min(1.0, len(content_lower.split()) / 50)  # Boost for longer content
                    
                    content_score = min(0.8, keyword_density * 1.5 * content_length_factor)
                    score = max(score, content_score)

            # Additional boost for high-confidence content indicators
            if section_type == "overview" and any(
                phrase in content_lower for phrase in [
                    "this product", "our platform", "the solution", "overview of",
                    "designed to", "provides", "enables", "helps users"
                ]
            ):
                score = max(score, 0.6)

            elif section_type == "users" and any(
                phrase in content_lower for phrase in [
                    "target users", "our users", "customers include", "user base",
                    "primary users", "secondary users", "user personas", "age", "demographics"
                ]
            ):
                score = max(score, 0.7)

            elif section_type == "technical" and any(
                phrase in content_lower for phrase in [
                    "built using", "technology stack", "database", "api", "framework",
                    "infrastructure", "deployment", "architecture", "microservices"
                ]
            ):
                score = max(score, 0.7)

            elif section_type == "business_model" and any(
                phrase in content_lower for phrase in [
                    "revenue model", "pricing strategy", "business model", "monetization",
                    "subscription", "freemium", "$", "cost", "price", "revenue"
                ]
            ):
                score = max(score, 0.7)

            if score > best_score:
                best_score = score
                best_type = section_type

        # Fallback semantic classification for unmatched sections
        if best_score < 0.3:
            fallback_type, fallback_score = self._semantic_fallback_classification(title, content)
            if fallback_score > best_score:
                best_type = fallback_type
                best_score = fallback_score

        return best_type, min(1.0, best_score)

    def _semantic_fallback_classification(self, title: str, content: str) -> Tuple[str, float]:
        """Fallback semantic classification for sections with unclear headers."""
        combined_text = f"{title} {content}".lower()
        
        # Semantic indicators with weighted scoring
        semantic_indicators = {
            "overview": {
                "strong": ["product overview", "executive summary", "introduction", "vision", "mission"],
                "medium": ["designed to", "provides", "enables", "platform", "solution"],
                "weak": ["about", "description", "purpose", "goal"]
            },
            "users": {
                "strong": ["target users", "user personas", "customers", "stakeholders"],
                "medium": ["demographics", "audience", "market segment", "user base"],
                "weak": ["who uses", "for users", "user"]
            },
            "requirements": {
                "strong": ["functional requirements", "features list", "core features"],
                "medium": ["capabilities", "functionality", "specifications", "must have"],
                "weak": ["features", "requirements", "scope"]
            },
            "technical": {
                "strong": ["technical architecture", "technology stack", "tech stack", "infrastructure", "deployment"],
                "medium": ["api design", "database", "security", "performance", "framework", "platform", "tools and technologies"],
                "weak": ["technical", "implementation", "system", "development", "hosting"]
            },
            "business_model": {
                "strong": ["business model", "revenue model", "pricing strategy"],
                "medium": ["monetization", "subscription", "freemium", "revenue"],
                "weak": ["business", "financial", "cost", "$"]
            },
            "competitive": {
                "strong": ["competitive analysis", "competitor research", "market analysis", "market competition"],
                "medium": ["alternatives", "similar products", "existing solutions", "competitive advantage"],
                "weak": ["competitive", "competitors", "competition", "market"]
            },
            "user_stories": {
                "strong": ["user stories", "use cases", "user journeys"],
                "medium": ["scenarios", "workflows", "user flows", "as a user"],
                "weak": ["stories", "use case", "scenario"]
            },
            "metrics": {
                "strong": ["success metrics", "kpi", "performance indicators"],
                "medium": ["goals", "objectives", "targets", "measurement"],
                "weak": ["metrics", "tracking", "analytics"]
            }
        }
        
        best_type = "other"
        best_score = 0.0
        
        for section_type, indicators in semantic_indicators.items():
            score = 0.0
            
            # Check strong indicators (weight: 0.8)
            for phrase in indicators["strong"]:
                if phrase in combined_text:
                    score = max(score, 0.8)
                    
            # Check medium indicators (weight: 0.6)
            for phrase in indicators["medium"]:
                if phrase in combined_text:
                    score = max(score, 0.6)
                    
            # Check weak indicators (weight: 0.4)
            for phrase in indicators["weak"]:
                if phrase in combined_text:
                    score = max(score, 0.4)
            
            if score > best_score:
                best_score = score
                best_type = section_type
                
        return best_type, best_score

    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract relevant keywords from section content."""
        # Simple keyword extraction based on frequency and relevance
        words = re.findall(r"\b[a-zA-Z]{3,}\b", content.lower())

        # Filter common words
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "who",
            "boy",
            "did",
            "its",
            "let",
            "put",
            "say",
            "she",
            "too",
            "use",
            "will",
            "this",
            "that",
            "with",
            "have",
            "from",
            "they",
            "been",
            "said",
            "each",
            "which",
            "their",
            "time",
            "would",
            "there",
            "could",
            "other",
            "make",
            "what",
            "know",
            "take",
            "than",
            "them",
            "well",
            "were",
            "way",
            "when",
            "where",
            "more",
            "some",
            "like",
            "into",
            "after",
            "back",
            "many",
        }

        # Count word frequencies
        word_freq: Dict[str, int] = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq > 1]

    def _extract_overview_content(self, content: str) -> str:
        """Extract and clean overview content."""
        # Remove markdown formatting and normalize
        clean_content = re.sub(
            r"\[([^\]]+)\]\([^\)]+\)", r"\1", content
        )  # Remove links
        clean_content = re.sub(
            r"[*_`]{1,3}([^*_`]+)[*_`]{1,3}", r"\1", clean_content
        )  # Remove formatting
        return clean_content.strip()[:1000]  # Limit length

    def _extract_users_content(self, content: str) -> str:
        """Extract target users information."""
        return self._extract_overview_content(content)[:500]

    def _extract_business_model_content(self, content: str) -> str:
        """Extract business model information."""
        return self._extract_overview_content(content)[:500]

    def _extract_technical_content(self, content: str) -> str:
        """Extract technical requirements content."""
        return self._extract_overview_content(content)[:1000]

    def _extract_competitive_content(self, content: str) -> str:
        """Extract competitive analysis content."""
        return self._extract_overview_content(content)[:1000]

    def _extract_user_stories_list(self, content: str) -> List[str]:
        """Extract user stories from content."""
        # Look for patterns like "As a... I want... So that..."
        user_story_pattern = r"(?:as\s+a\s+.+?i\s+want\s+.+?(?:so\s+that\s+.+?)?)"
        stories = re.findall(
            user_story_pattern, content.lower(), re.IGNORECASE | re.DOTALL
        )

        # Also look for bullet points that might be user stories
        bullet_points = re.findall(r"^[*\-+]\s+(.+)$", content, re.MULTILINE)
        user_stories = [
            story.strip() for story in bullet_points if len(story.strip()) > 20
        ]

        return list(set(stories + user_stories))[:10]  # Limit and deduplicate

    def _extract_metrics_list(self, content: str) -> List[str]:
        """Extract success metrics from content."""
        # Look for metric patterns
        metrics = []

        # Bullet points that might be metrics
        bullet_points = re.findall(r"^[*\-+]\s+(.+)$", content, re.MULTILINE)
        for point in bullet_points:
            if any(
                keyword in point.lower()
                for keyword in [
                    "%",
                    "increase",
                    "decrease",
                    "improve",
                    "measure",
                    "kpi",
                    "metric",
                ]
            ):
                metrics.append(point.strip())

        return metrics[:10]

    def _extract_requirements_lists(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract functional and non-functional requirements."""
        functional = []
        non_functional = []

        # Extract bullet points
        bullet_points = re.findall(r"^[*\-+]\s+(.+)$", content, re.MULTILINE)

        for point in bullet_points:
            point_lower = point.lower()
            if any(
                keyword in point_lower
                for keyword in ["performance", "security", "scalability", "reliability"]
            ):
                non_functional.append(point.strip())
            else:
                functional.append(point.strip())

        return functional[:15], non_functional[:10]

    def _extract_assumptions(self, sections: List[PRDSection]) -> List[str]:
        """Extract assumptions from all sections."""
        assumptions = []
        for section in sections:
            if (
                "assumption" in section.title.lower()
                or "assume" in section.content.lower()
            ):
                # Extract bullet points that might be assumptions
                bullets = re.findall(r"^[*\-+]\s+(.+)$", section.content, re.MULTILINE)
                assumptions.extend([a.strip() for a in bullets])
        return assumptions[:10]

    def _extract_constraints(self, sections: List[PRDSection]) -> List[str]:
        """Extract constraints from all sections."""
        constraints = []
        for section in sections:
            if any(
                keyword in section.title.lower()
                for keyword in ["constraint", "limitation", "restriction"]
            ):
                bullets = re.findall(r"^[*\-+]\s+(.+)$", section.content, re.MULTILINE)
                constraints.extend([c.strip() for c in bullets])
        return constraints[:10]

    def _extract_risks(self, sections: List[PRDSection]) -> List[str]:
        """Extract risks from all sections."""
        risks = []
        for section in sections:
            if "risk" in section.title.lower() or "risk" in section.content.lower():
                bullets = re.findall(r"^[*\-+]\s+(.+)$", section.content, re.MULTILINE)
                risks.extend([r.strip() for r in bullets if "risk" in r.lower()])
        return risks[:10]

    def _extract_timeline_info(self, sections: List[PRDSection]) -> Optional[str]:
        """Extract timeline information."""
        for section in sections:
            if any(
                keyword in section.title.lower()
                for keyword in ["timeline", "schedule", "roadmap"]
            ):
                return section.content[:500]
        return None

    def _extract_budget_info(self, sections: List[PRDSection]) -> Optional[str]:
        """Extract budget information."""
        for section in sections:
            if any(
                keyword in section.title.lower()
                for keyword in ["budget", "cost", "financial"]
            ):
                return section.content[:300]
        return None

    def _analyze_prd_section_coverage(
        self, sections: List[PRDSection]
    ) -> Dict[str, float]:
        """Analyze coverage provided by PRD sections for different gap categories."""
        coverage = {
            "business_model": 0.0,
            "technical_requirements": 0.0,
            "user_experience": 0.0,
            "integration": 0.0,
            "validation": 0.0,
            "deployment": 0.0,
            "goal_definition": 0.0,
        }

        for section in sections:
            section_weight = (
                min(1.0, section.word_count / 100) * section.confidence_score
            )

            if section.section_type == "business_model":
                coverage["business_model"] = max(
                    coverage["business_model"], section_weight
                )
            elif section.section_type == "technical":
                coverage["technical_requirements"] = max(
                    coverage["technical_requirements"], section_weight
                )
            elif (
                section.section_type == "users"
                or section.section_type == "user_stories"
            ):
                coverage["user_experience"] = max(
                    coverage["user_experience"], section_weight
                )
            elif section.section_type == "requirements":
                coverage["integration"] = max(
                    coverage["integration"], section_weight * 0.6
                )
                coverage["validation"] = max(
                    coverage["validation"], section_weight * 0.4
                )
            elif section.section_type == "overview":
                coverage["goal_definition"] = max(
                    coverage["goal_definition"], section_weight
                )

        return coverage

    def _calculate_content_quality(
        self, sections: List[PRDSection], raw_content: str
    ) -> float:
        """Calculate overall content quality score."""
        if not sections:
            return 0.0

        # Factors for quality assessment
        section_count_score = min(1.0, len(sections) / 5.0)  # 5 sections = full score

        avg_confidence = sum(s.confidence_score for s in sections) / len(sections)

        total_words = sum(s.word_count for s in sections)
        word_count_score = min(1.0, total_words / 1000)  # 1000 words = full score

        structure_score = min(
            1.0, len([s for s in sections if s.section_level <= 2]) / 3.0
        )

        # Combine factors
        quality_score = (
            section_count_score * 0.25
            + avg_confidence * 0.35
            + word_count_score * 0.25
            + structure_score * 0.15
        ) * 10.0

        return min(10.0, quality_score)
