"""Gap analysis service for identifying knowledge gaps in business concepts."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

from ..models.business_concept import BusinessConceptRequest
from ..models.gap_analysis import KnowledgeGap, GapAnalysisResult
from ..services.research_service import ResearchContext
from ..utils.domain_knowledge_base import DomainKnowledgeBase

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
