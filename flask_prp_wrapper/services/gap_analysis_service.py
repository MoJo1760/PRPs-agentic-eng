"""Gap analysis service for identifying knowledge gaps in business concepts."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

from ..models.business_concept import BusinessConceptRequest
from ..models.gap_analysis import KnowledgeGap, GapAnalysisResult
from ..services.research_service import ResearchContext
from ..utils.domain_knowledge_base import DomainKnowledgeBase
from ..models.prd_document import PRDDocument, PRDSection

logger = logging.getLogger(__name__)


class GapAnalysisService:
    """Service for analyzing business concepts and identifying knowledge gaps."""

    def __init__(self, domain_knowledge_base: Optional[DomainKnowledgeBase] = None):
        """Initialize the gap analysis service.

        Args:
            domain_knowledge_base: Domain knowledge base for requirements
        """
        self.domain_kb = domain_knowledge_base or DomainKnowledgeBase()
        self._analysis_cache: Dict[str, GapAnalysisResult] = {}

        # Keywords that indicate coverage in different areas
        self._coverage_indicators = {
            "business_model": [
                "pricing",
                "revenue",
                "subscription",
                "monetization",
                "business model",
                "customers",
                "market",
                "value proposition",
                "cost structure",
            ],
            "technical_requirements": [
                "architecture",
                "database",
                "API",
                "security",
                "authentication",
                "scalability",
                "performance",
                "infrastructure",
                "technology stack",
            ],
            "user_experience": [
                "user interface",
                "UI",
                "UX",
                "design",
                "navigation",
                "user flow",
                "mobile",
                "responsive",
                "accessibility",
                "usability",
            ],
            "integration": [
                "third-party",
                "integration",
                "API",
                "webhook",
                "external service",
                "payment gateway",
                "email service",
                "analytics",
                "monitoring",
            ],
            "validation": [
                "testing",
                "validation",
                "quality assurance",
                "monitoring",
                "logging",
                "error handling",
                "debugging",
                "performance testing",
            ],
            "deployment": [
                "deployment",
                "hosting",
                "infrastructure",
                "DevOps",
                "CI/CD",
                "containerization",
                "cloud",
                "scaling",
                "production",
            ],
        }

    async def analyze_concept_gaps(
        self,
        concept: BusinessConceptRequest,
        existing_research: Optional[ResearchContext] = None,
        questionnaire_responses: Optional[List] = None,
    ) -> GapAnalysisResult:
        """Analyze a business concept for knowledge gaps.

        Args:
            concept: Business concept to analyze
            existing_research: Any existing research context
            questionnaire_responses: Previous questionnaire responses

        Returns:
            Gap analysis result with identified gaps and coverage metrics
        """
        # Generate cache key
        cache_key = self._generate_cache_key(
            concept, existing_research, questionnaire_responses
        )

        # Check cache
        if cache_key in self._analysis_cache:
            logger.info(f"Returning cached gap analysis for concept {concept.title}")
            return self._analysis_cache[cache_key]

        logger.info(f"Analyzing gaps for concept: {concept.title}")

        # Get domain requirements
        domain = concept.domain.value if concept.domain else "general"
        domain_requirements = self.domain_kb.get_domain_requirements(domain)

        # Analyze current coverage
        current_coverage = self._analyze_current_coverage(
            concept, existing_research, questionnaire_responses
        )

        # Identify gaps
        identified_gaps = []
        gap_id_counter = 0

        for requirement in domain_requirements:
            gap_severity = self._assess_requirement_gap(
                requirement, current_coverage, concept
            )

            if gap_severity > 0.3:  # Threshold for considering it a gap
                gap = KnowledgeGap(
                    id=f"gap_{concept.title[:20]}_{gap_id_counter}_{requirement.category}",
                    domain=domain,
                    category=requirement.category,
                    description=f"Missing or insufficient information about: {requirement.requirement}",
                    priority=requirement.priority,
                    identified_at=datetime.utcnow(),
                    confidence_score=gap_severity,
                )
                identified_gaps.append(gap)
                gap_id_counter += 1

        # Add context-specific gaps
        context_gaps = self._identify_context_specific_gaps(concept, current_coverage)
        identified_gaps.extend(context_gaps)

        # Calculate coverage metrics
        coverage_percentage = self._calculate_overall_coverage(
            domain_requirements, current_coverage
        )

        domain_completeness = self._calculate_domain_completeness(
            domain_requirements, current_coverage
        )

        # Prioritize research areas
        next_research_areas = self._prioritize_research_areas(identified_gaps)

        # Count gaps by priority
        critical_gaps = len([g for g in identified_gaps if g.priority == "critical"])
        high_priority_gaps = len([g for g in identified_gaps if g.priority == "high"])

        result = GapAnalysisResult(
            concept_id=f"concept_{hashlib.md5(concept.title.encode()).hexdigest()[:8]}",
            identified_gaps=identified_gaps,
            coverage_percentage=coverage_percentage,
            domain_completeness=domain_completeness,
            analysis_timestamp=datetime.utcnow(),
            next_research_areas=next_research_areas,
            critical_gaps_count=critical_gaps,
            high_priority_gaps_count=high_priority_gaps,
        )

        # Cache result
        self._analysis_cache[cache_key] = result

        logger.info(
            f"Gap analysis complete: {len(identified_gaps)} gaps identified, "
            f"{coverage_percentage:.1f}% coverage"
        )

        return result

    def _generate_cache_key(
        self,
        concept: BusinessConceptRequest,
        existing_research: Optional[ResearchContext],
        questionnaire_responses: Optional[List],
    ) -> str:
        """Generate cache key for analysis result."""
        key_parts = [
            concept.title,
            concept.description,
            str(concept.domain),
            str(concept.business_model),
        ]

        if existing_research:
            key_parts.append(str(existing_research.research_timestamp))

        if questionnaire_responses:
            key_parts.append(str(len(questionnaire_responses)))

        key_string = "_".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _analyze_current_coverage(
        self,
        concept: BusinessConceptRequest,
        existing_research: Optional[ResearchContext],
        questionnaire_responses: Optional[List],
    ) -> Dict[str, float]:
        """Analyze current coverage across different areas.

        Returns:
            Dictionary mapping coverage areas to coverage scores (0-1)
        """
        coverage: Dict[str, float] = {}

        # Analyze concept description coverage
        description_coverage = self._analyze_text_coverage(concept.description)

        # Analyze existing research coverage
        research_coverage = {}
        if existing_research:
            research_coverage = self._analyze_research_coverage(existing_research)

        # Analyze questionnaire response coverage
        response_coverage = {}
        if questionnaire_responses:
            response_coverage = self._analyze_response_coverage(questionnaire_responses)

        # Combine coverage scores
        all_areas = (
            set(description_coverage.keys())
            | set(research_coverage.keys())
            | set(response_coverage.keys())
        )

        for area in all_areas:
            desc_score = description_coverage.get(area, 0.0)
            research_score = research_coverage.get(area, 0.0)
            response_score = response_coverage.get(area, 0.0)

            # Weighted combination - responses carry more weight than description
            coverage[area] = (
                desc_score * 0.3 + research_score * 0.4 + response_score * 0.3
            )

        return coverage

    def _analyze_text_coverage(self, text: str) -> Dict[str, float]:
        """Analyze text coverage across different areas."""
        text_lower = text.lower()
        coverage = {}

        for area, keywords in self._coverage_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by number of keywords and text length
            coverage_score = min(matches / len(keywords), 1.0)
            # Boost score if text is detailed
            if len(text) > 200:
                coverage_score *= 1.2
            coverage[area] = min(coverage_score, 1.0)

        return coverage

    def _analyze_research_coverage(self, research: ResearchContext) -> Dict[str, float]:
        """Analyze coverage from existing research context."""
        coverage = {}

        # Analyze technical patterns coverage
        if research.technical_patterns:
            tech_coverage = (
                len(research.technical_patterns) / 5.0
            )  # Assume 5 is good coverage
            coverage["technical_requirements"] = min(tech_coverage, 1.0)

        # Analyze best practices coverage
        if research.best_practices:
            practices_coverage = len(research.best_practices) / 3.0
            coverage["validation"] = min(practices_coverage, 1.0)

        # Analyze competitor analysis coverage
        if research.competitor_analysis:
            business_coverage = len(research.competitor_analysis) / 3.0
            coverage["business_model"] = min(business_coverage, 1.0)

        # Analyze recommended technologies coverage
        if research.recommended_technologies:
            integration_coverage = len(research.recommended_technologies) / 4.0
            coverage["integration"] = min(integration_coverage, 1.0)

        return coverage

    def _analyze_response_coverage(self, responses: List) -> Dict[str, float]:
        """Analyze coverage from questionnaire responses."""
        coverage = {}

        if not responses:
            return coverage

        # Analyze response content for coverage indicators
        all_response_text = " ".join([str(resp) for resp in responses])
        return self._analyze_text_coverage(all_response_text)

    def _assess_requirement_gap(
        self,
        requirement,
        current_coverage: Dict[str, float],
        concept: BusinessConceptRequest,
    ) -> float:
        """Assess the gap severity for a specific requirement.

        Returns:
            Gap severity score (0-1, where 1 is maximum gap)
        """
        category_coverage = current_coverage.get(requirement.category, 0.0)

        # Adjust based on requirement priority
        priority_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}

        weight = priority_weights.get(requirement.priority, 0.6)

        # Calculate gap (inverse of coverage)
        gap_score = (1.0 - category_coverage) * weight

        # Domain-specific adjustments
        domain = concept.domain.value if concept.domain else "general"
        if (
            domain in ["fintech", "healthcare"]
            and requirement.category == "technical_requirements"
        ):
            gap_score *= 1.2  # These domains need extra technical coverage

        return min(gap_score, 1.0)

    def _identify_context_specific_gaps(
        self, concept: BusinessConceptRequest, current_coverage: Dict[str, float]
    ) -> List[KnowledgeGap]:
        """Identify gaps specific to the business concept context."""
        context_gaps = []

        # Check for missing business model information
        if not concept.business_model:
            gap = KnowledgeGap(
                id=f"context_business_model_{datetime.utcnow().strftime('%H%M%S')}",
                domain=concept.domain.value if concept.domain else "general",
                category="business_model",
                description="Business model not specified - need to understand monetization strategy",
                priority="high",
                confidence_score=0.9,
            )
            context_gaps.append(gap)

        # Check for missing target users
        if not concept.target_users:
            gap = KnowledgeGap(
                id=f"context_target_users_{datetime.utcnow().strftime('%H%M%S')}",
                domain=concept.domain.value if concept.domain else "general",
                category="user_experience",
                description="Target users not clearly defined - need user persona details",
                priority="high",
                confidence_score=0.8,
            )
            context_gaps.append(gap)

        # Check for vague descriptions
        if len(concept.description) < 100:
            gap = KnowledgeGap(
                id=f"context_description_{datetime.utcnow().strftime('%H%M%S')}",
                domain=concept.domain.value if concept.domain else "general",
                category="goal_definition",
                description="Concept description too brief - need more detailed requirements",
                priority="medium",
                confidence_score=0.7,
            )
            context_gaps.append(gap)

        return context_gaps

    def _calculate_overall_coverage(
        self, domain_requirements, current_coverage: Dict[str, float]
    ) -> float:
        """Calculate overall coverage percentage."""
        if not domain_requirements:
            return 0.0

        total_weight = sum(req.coverage_weight for req in domain_requirements)
        weighted_coverage = 0.0

        for requirement in domain_requirements:
            category_coverage = current_coverage.get(requirement.category, 0.0)
            weighted_coverage += category_coverage * requirement.coverage_weight

        return (weighted_coverage / total_weight) * 100 if total_weight > 0 else 0.0

    def _calculate_domain_completeness(
        self, domain_requirements, current_coverage: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate completeness by domain area."""
        completeness = {}

        # Group requirements by category
        category_requirements: Dict[str, List] = {}
        for req in domain_requirements:
            if req.category not in category_requirements:
                category_requirements[req.category] = []
            category_requirements[req.category].append(req)

        # Calculate completeness for each category
        for category, reqs in category_requirements.items():
            category_coverage = current_coverage.get(category, 0.0)
            completeness[category] = category_coverage * 100

        return completeness

    def _prioritize_research_areas(self, gaps: List[KnowledgeGap]) -> List[str]:
        """Prioritize research areas based on identified gaps."""
        # Count gaps by category and priority
        category_priority_score = {}

        for gap in gaps:
            if gap.category not in category_priority_score:
                category_priority_score[gap.category] = 0.0

            # Score based on priority
            priority_scores = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}

            score = priority_scores.get(gap.priority, 2.0)
            score *= gap.confidence_score  # Weight by confidence
            category_priority_score[gap.category] += score

        # Sort categories by score
        sorted_categories = sorted(
            category_priority_score.items(), key=lambda x: x[1], reverse=True
        )

        return [category for category, _ in sorted_categories]

    async def update_gap_status(
        self,
        gap_id: str,
        filled: bool,
        confidence_score: Optional[float] = None,
        research_sources: Optional[List[str]] = None,
    ) -> bool:
        """Update the status of a knowledge gap.

        Args:
            gap_id: ID of the gap to update
            filled: Whether the gap has been filled
            confidence_score: Updated confidence score
            research_sources: Sources used to fill the gap

        Returns:
            True if gap was updated successfully
        """
        # In a real implementation, this would update persistent storage
        # For now, we'll update any cached results

        updated = False
        for analysis_result in self._analysis_cache.values():
            for gap in analysis_result.identified_gaps:
                if gap.id == gap_id:
                    gap.filled = filled
                    if confidence_score is not None:
                        gap.confidence_score = confidence_score
                    if research_sources:
                        gap.research_sources.extend(research_sources)
                    updated = True
                    break

        if updated:
            logger.info(f"Updated gap {gap_id}: filled={filled}")
        else:
            logger.warning(f"Gap {gap_id} not found for update")

        return updated

    def get_gap_summary(self, concept_id: str) -> Optional[Dict]:
        """Get summary of gaps for a concept.

        Args:
            concept_id: Concept ID to get gaps for

        Returns:
            Summary of gaps or None if not found
        """
        for analysis_result in self._analysis_cache.values():
            if analysis_result.concept_id == concept_id:
                return {
                    "total_gaps": len(analysis_result.identified_gaps),
                    "filled_gaps": len(
                        [g for g in analysis_result.identified_gaps if g.filled]
                    ),
                    "critical_gaps": analysis_result.critical_gaps_count,
                    "high_priority_gaps": analysis_result.high_priority_gaps_count,
                    "coverage_percentage": analysis_result.coverage_percentage,
                    "next_research_areas": analysis_result.next_research_areas[:3],
                }

        return None

    async def analyze_concept_gaps_with_prd(
        self,
        concept: BusinessConceptRequest,
        prd_document: Optional[PRDDocument] = None,
        existing_research: Optional[ResearchContext] = None,
        questionnaire_responses: Optional[List] = None,
    ) -> GapAnalysisResult:
        """Enhanced gap analysis incorporating PRD content.

        Args:
            concept: Business concept to analyze
            prd_document: Associated PRD document (optional)
            existing_research: Any existing research context
            questionnaire_responses: Previous questionnaire responses

        Returns:
            Gap analysis result with PRD-enhanced coverage metrics
        """
        logger.info(f"Analyzing gaps with PRD for concept: {concept.title}")

        # Generate enhanced cache key that includes PRD
        cache_key = self._generate_enhanced_cache_key(
            concept, prd_document, existing_research, questionnaire_responses
        )

        # Check cache
        if cache_key in self._analysis_cache:
            logger.info(
                f"Returning cached PRD-enhanced gap analysis for concept {concept.title}"
            )
            return self._analysis_cache[cache_key]

        # Get domain requirements
        domain = concept.domain.value if concept.domain else "general"
        domain_requirements = self.domain_kb.get_domain_requirements(domain)

        # Analyze current coverage including PRD content
        current_coverage = self._analyze_current_coverage_with_prd(
            concept, prd_document, existing_research, questionnaire_responses
        )

        # Identify remaining gaps after PRD integration
        identified_gaps = []
        gap_id_counter = 0

        for requirement in domain_requirements:
            gap_severity = self._assess_requirement_gap_with_prd(
                requirement, current_coverage, concept, prd_document
            )

            if gap_severity > 0.3:  # Threshold for considering it a gap
                gap = KnowledgeGap(
                    id=f"gap_prd_{concept.title[:20]}_{gap_id_counter}_{requirement.category}",
                    domain=domain,
                    category=requirement.category,
                    description=f"Missing or insufficient information about: {requirement.requirement}",
                    priority=requirement.priority,
                    identified_at=datetime.utcnow(),
                    confidence_score=gap_severity,
                )
                identified_gaps.append(gap)
                gap_id_counter += 1

        # Add context-specific gaps (reduced if PRD covers areas)
        context_gaps = self._identify_context_specific_gaps_with_prd(
            concept, current_coverage, prd_document
        )
        identified_gaps.extend(context_gaps)

        # Calculate enhanced coverage metrics
        coverage_percentage = self._calculate_overall_coverage(
            domain_requirements, current_coverage
        )

        domain_completeness = self._calculate_domain_completeness(
            domain_requirements, current_coverage
        )

        # Prioritize research areas based on remaining gaps
        next_research_areas = self._prioritize_research_areas_with_prd(
            identified_gaps, prd_document
        )

        # Count gaps by priority
        critical_gaps = len([g for g in identified_gaps if g.priority == "critical"])
        high_priority_gaps = len([g for g in identified_gaps if g.priority == "high"])

        result = GapAnalysisResult(
            concept_id=f"concept_prd_{hashlib.md5(concept.title.encode()).hexdigest()[:8]}",
            identified_gaps=identified_gaps,
            coverage_percentage=coverage_percentage,
            domain_completeness=domain_completeness,
            analysis_timestamp=datetime.utcnow(),
            next_research_areas=next_research_areas,
            critical_gaps_count=critical_gaps,
            high_priority_gaps_count=high_priority_gaps,
        )

        # Cache result
        self._analysis_cache[cache_key] = result

        logger.info(
            f"PRD-enhanced gap analysis complete: {len(identified_gaps)} gaps identified, "
            f"{coverage_percentage:.1f}% coverage (PRD: {'Yes' if prd_document else 'No'})"
        )

        return result

    def _analyze_current_coverage_with_prd(
        self,
        concept: BusinessConceptRequest,
        prd_document: Optional[PRDDocument],
        existing_research: Optional[ResearchContext],
        questionnaire_responses: Optional[List],
    ) -> Dict[str, float]:
        """Analyze current coverage including PRD content.

        Returns:
            Dictionary mapping coverage areas to coverage scores (0-1)
        """
        # Start with base coverage analysis
        base_coverage = self._analyze_current_coverage(
            concept, existing_research, questionnaire_responses
        )

        # If PRD available, analyze and merge PRD coverage
        if prd_document:
            prd_coverage = self._analyze_prd_coverage(prd_document)
            # Merge coverage, taking the maximum of base and PRD coverage
            enhanced_coverage = {}
            all_areas = set(base_coverage.keys()) | set(prd_coverage.keys())

            for area in all_areas:
                base_score = base_coverage.get(area, 0.0)
                prd_score = prd_coverage.get(area, 0.0)
                # Use weighted combination favoring PRD when it's higher quality
                enhanced_coverage[area] = max(
                    base_score, prd_score * 0.9
                )  # PRD gets slight discount for parsing uncertainty

            return enhanced_coverage

        return base_coverage

    def _analyze_prd_coverage(self, prd_document: PRDDocument) -> Dict[str, float]:
        """Analyze coverage provided by PRD sections.

        Args:
            prd_document: PRD document to analyze

        Returns:
            Dictionary mapping coverage areas to scores (0-1)
        """
        coverage = {}

        for section in prd_document.sections:
            section_coverage = self._calculate_section_coverage_contribution(section)

            # Map section types to coverage areas
            if section.section_type == "overview":
                coverage["goal_definition"] = max(
                    coverage.get("goal_definition", 0.0), section_coverage
                )

            elif section.section_type == "users":
                coverage["user_experience"] = max(
                    coverage.get("user_experience", 0.0), section_coverage
                )

            elif section.section_type == "business_model":
                coverage["business_model"] = max(
                    coverage.get("business_model", 0.0), section_coverage
                )

            elif section.section_type == "technical":
                coverage["technical_requirements"] = max(
                    coverage.get("technical_requirements", 0.0), section_coverage
                )

            elif section.section_type == "requirements":
                coverage["technical_requirements"] = max(
                    coverage.get("technical_requirements", 0.0), section_coverage * 0.8
                )
                coverage["integration"] = max(
                    coverage.get("integration", 0.0), section_coverage * 0.6
                )

            elif section.section_type == "user_stories":
                coverage["user_experience"] = max(
                    coverage.get("user_experience", 0.0), section_coverage * 0.7
                )

            elif section.section_type == "metrics":
                coverage["validation"] = max(
                    coverage.get("validation", 0.0), section_coverage * 0.6
                )

            elif section.section_type == "competitive":
                coverage["business_model"] = max(
                    coverage.get("business_model", 0.0), section_coverage * 0.5
                )

        return coverage

    def _calculate_section_coverage_contribution(self, section: PRDSection) -> float:
        """Calculate how much a PRD section contributes to coverage.

        Args:
            section: PRD section to analyze

        Returns:
            Coverage contribution score (0-1)
        """
        # Base score from confidence and word count
        base_score = section.confidence_score

        # Adjust based on content quality indicators
        word_count_factor = min(1.0, section.word_count / 100)  # Optimal at 100+ words

        # Boost for detailed sections
        if section.word_count > 200:
            base_score *= 1.1

        # Boost for high-confidence classifications
        if section.confidence_score > 0.8:
            base_score *= 1.05

        # Consider keyword richness
        keyword_factor = min(
            1.0, len(section.extracted_keywords) / 5
        )  # Optimal at 5+ keywords

        final_score = base_score * word_count_factor * (0.8 + keyword_factor * 0.2)

        return min(1.0, final_score)

    def _assess_requirement_gap_with_prd(
        self,
        requirement,
        current_coverage: Dict[str, float],
        concept: BusinessConceptRequest,
        prd_document: Optional[PRDDocument],
    ) -> float:
        """Assess requirement gap severity with PRD context.

        Returns:
            Gap severity score (0-1, where 1 is maximum gap)
        """
        # Base gap assessment
        base_gap = self._assess_requirement_gap(requirement, current_coverage, concept)

        # If PRD is available, check if it specifically addresses this requirement
        if prd_document:
            prd_addresses_requirement = self._prd_addresses_requirement(
                prd_document, requirement
            )

            if prd_addresses_requirement > 0.5:
                # PRD significantly addresses this requirement, reduce gap
                base_gap *= 1.0 - prd_addresses_requirement * 0.5

        return base_gap

    def _prd_addresses_requirement(
        self, prd_document: PRDDocument, requirement
    ) -> float:
        """Check if PRD content addresses a specific requirement.

        Returns:
            Score (0-1) indicating how well PRD addresses the requirement
        """
        requirement_keywords = requirement.requirement.lower().split()
        total_relevance = 0.0

        for section in prd_document.sections:
            section_relevance = 0.0
            section_content = section.content.lower()

            # Check for keyword matches
            matched_keywords = sum(
                1 for keyword in requirement_keywords if keyword in section_content
            )
            if requirement_keywords:
                keyword_match_score = matched_keywords / len(requirement_keywords)
                section_relevance = keyword_match_score * section.confidence_score

            total_relevance = max(total_relevance, section_relevance)

        return min(1.0, total_relevance)

    def _identify_context_specific_gaps_with_prd(
        self,
        concept: BusinessConceptRequest,
        current_coverage: Dict[str, float],
        prd_document: Optional[PRDDocument],
    ) -> List[KnowledgeGap]:
        """Identify context-specific gaps considering PRD content.

        Returns:
            List of context-specific knowledge gaps
        """
        context_gaps = []

        # Check for missing business model information (reduced if PRD has it)
        if not concept.business_model:
            business_model_covered = False
            if prd_document:
                business_model_covered = any(
                    s.section_type == "business_model" and s.word_count > 50
                    for s in prd_document.sections
                )

            if not business_model_covered:
                gap = KnowledgeGap(
                    id=f"context_business_model_prd_{datetime.utcnow().strftime('%H%M%S')}",
                    domain=concept.domain.value if concept.domain else "general",
                    category="business_model",
                    description="Business model not specified and not covered in PRD - need monetization strategy",
                    priority="high",
                    confidence_score=0.9,
                )
                context_gaps.append(gap)

        # Check for missing target users (reduced if PRD has it)
        if not concept.target_users:
            users_covered = False
            if prd_document:
                users_covered = any(
                    s.section_type == "users" and s.word_count > 30
                    for s in prd_document.sections
                )

            if not users_covered:
                gap = KnowledgeGap(
                    id=f"context_target_users_prd_{datetime.utcnow().strftime('%H%M%S')}",
                    domain=concept.domain.value if concept.domain else "general",
                    category="user_experience",
                    description="Target users not defined in concept or PRD - need user persona details",
                    priority="high",
                    confidence_score=0.8,
                )
                context_gaps.append(gap)

        # Check for vague descriptions (PRD can help here)
        if len(concept.description) < 100:
            overview_covered = False
            if prd_document:
                overview_covered = any(
                    s.section_type == "overview" and s.word_count > 100
                    for s in prd_document.sections
                )

            if not overview_covered:
                gap = KnowledgeGap(
                    id=f"context_description_prd_{datetime.utcnow().strftime('%H%M%S')}",
                    domain=concept.domain.value if concept.domain else "general",
                    category="goal_definition",
                    description="Concept description too brief and PRD lacks detailed overview",
                    priority="medium",
                    confidence_score=0.7,
                )
                context_gaps.append(gap)

        return context_gaps

    def _prioritize_research_areas_with_prd(
        self,
        gaps: List[KnowledgeGap],
        prd_document: Optional[PRDDocument],
    ) -> List[str]:
        """Prioritize research areas considering PRD coverage.

        Returns:
            List of prioritized research area categories
        """
        # Base prioritization
        base_priorities = self._prioritize_research_areas(gaps)

        if not prd_document:
            return base_priorities

        # Adjust priorities based on PRD coverage
        prd_covered_areas = {
            s.section_type for s in prd_document.sections if s.word_count > 50
        }

        # Boost priority for areas not covered by PRD
        area_mapping = {
            "business_model": "business_model",
            "technical_requirements": "technical",
            "user_experience": "users",
            "integration": "requirements",
            "validation": "metrics",
        }

        enhanced_priorities = []
        for area in base_priorities:
            prd_section_type = area_mapping.get(area)
            if prd_section_type and prd_section_type not in prd_covered_areas:
                # Area not covered by PRD, higher priority for research
                enhanced_priorities.insert(0, area)  # Move to front
            else:
                enhanced_priorities.append(area)

        return enhanced_priorities

    def _generate_enhanced_cache_key(
        self,
        concept: BusinessConceptRequest,
        prd_document: Optional[PRDDocument],
        existing_research: Optional[ResearchContext],
        questionnaire_responses: Optional[List],
    ) -> str:
        """Generate cache key that includes PRD document information."""
        key_parts = [
            concept.title,
            concept.description,
            str(concept.domain),
            str(concept.business_model),
        ]

        if prd_document:
            key_parts.extend(
                [
                    prd_document.document_id,
                    str(prd_document.extraction_quality_score),
                    str(len(prd_document.sections)),
                ]
            )

        if existing_research:
            key_parts.append(str(existing_research.research_timestamp))

        if questionnaire_responses:
            key_parts.append(str(len(questionnaire_responses)))

        key_string = "_".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
