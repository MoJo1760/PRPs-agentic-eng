"""Coverage validation service for determining research completeness."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..models.gap_analysis import GapAnalysisResult, KnowledgeGap
from ..models.coverage_metrics import (
    CoverageGate,
    StoppingCriteria,
    DetailedCoverageMetrics,
    CoverageAssessmentResult,
)
from ..utils.domain_knowledge_base import DomainKnowledgeBase

logger = logging.getLogger(__name__)


class CoverageValidator:
    """Service for validating requirement coverage completeness and determining stopping criteria."""

    def __init__(
        self,
        domain_knowledge_base: Optional[DomainKnowledgeBase] = None,
        default_stopping_criteria: Optional[StoppingCriteria] = None,
    ):
        """Initialize the coverage validator.

        Args:
            domain_knowledge_base: Domain knowledge base for requirements
            default_stopping_criteria: Default stopping criteria configuration
        """
        self.domain_kb = domain_knowledge_base or DomainKnowledgeBase()
        self.default_stopping_criteria = default_stopping_criteria or StoppingCriteria(
            minimum_overall_coverage=95.0,
            minimum_domain_coverage=85.0,
            minimum_critical_gaps_filled=100.0,
            minimum_high_priority_gaps_filled=90.0,
            required_quality_gates=["technical_completeness", "business_model_clarity"],
            maximum_iterations=5,
            maximum_time_minutes=15.0,
            minimum_official_source_ratio=0.8,
        )

        # Define quality gates
        self._quality_gates = self._initialize_quality_gates()

    def _initialize_quality_gates(self) -> List[CoverageGate]:
        """Initialize standard quality gates for coverage validation."""
        return [
            CoverageGate(
                gate_name="technical_completeness",
                description="Technical requirements are sufficiently detailed",
                threshold=85.0,
                required_for_completion=True,
                validation_rules=[
                    "Architecture approach specified",
                    "Technology stack identified",
                    "Security considerations addressed",
                    "Performance requirements defined",
                ],
            ),
            CoverageGate(
                gate_name="business_model_clarity",
                description="Business model and monetization strategy are clear",
                threshold=90.0,
                required_for_completion=True,
                validation_rules=[
                    "Revenue model specified",
                    "Target market identified",
                    "Value proposition articulated",
                    "Cost structure considered",
                ],
            ),
            CoverageGate(
                gate_name="user_experience_definition",
                description="User experience and interaction patterns are defined",
                threshold=80.0,
                required_for_completion=False,
                validation_rules=[
                    "User personas defined",
                    "User journeys mapped",
                    "Interface patterns specified",
                    "Accessibility considerations included",
                ],
            ),
            CoverageGate(
                gate_name="integration_requirements",
                description="External integrations and dependencies are identified",
                threshold=75.0,
                required_for_completion=False,
                validation_rules=[
                    "Third-party services identified",
                    "API requirements specified",
                    "Data flow defined",
                    "Error handling considered",
                ],
            ),
            CoverageGate(
                gate_name="validation_strategy",
                description="Testing and validation approach is comprehensive",
                threshold=70.0,
                required_for_completion=True,
                validation_rules=[
                    "Testing strategy defined",
                    "Validation commands provided",
                    "Quality metrics specified",
                    "Monitoring approach outlined",
                ],
            ),
        ]

    async def validate_coverage(
        self,
        gap_analysis: GapAnalysisResult,
        research_quality_score: float = 0.0,
        iteration_count: int = 0,
        elapsed_time_minutes: float = 0.0,
        official_source_ratio: float = 0.0,
        stopping_criteria: Optional[StoppingCriteria] = None,
    ) -> CoverageAssessmentResult:
        """Validate coverage completeness and determine if research should continue.

        Args:
            gap_analysis: Current gap analysis result
            research_quality_score: Quality score of research conducted
            iteration_count: Number of iterations completed
            elapsed_time_minutes: Time elapsed in research process
            official_source_ratio: Ratio of official to total sources used
            stopping_criteria: Custom stopping criteria (uses default if None)

        Returns:
            Coverage assessment result with continuation decision
        """
        criteria = stopping_criteria or self.default_stopping_criteria

        logger.info(
            f"Validating coverage for concept {gap_analysis.concept_id}: "
            f"{gap_analysis.coverage_percentage:.1f}% coverage, "
            f"{len(gap_analysis.identified_gaps)} gaps"
        )

        # Calculate detailed coverage metrics
        coverage_metrics = await self._calculate_detailed_coverage_metrics(
            gap_analysis, research_quality_score, official_source_ratio
        )

        # Evaluate quality gates
        updated_quality_gates = self._evaluate_quality_gates(
            gap_analysis, coverage_metrics
        )
        coverage_metrics.quality_gates = updated_quality_gates

        # Determine if stopping criteria are met
        should_continue, stop_reason = self._evaluate_stopping_criteria(
            gap_analysis,
            coverage_metrics,
            criteria,
            iteration_count,
            elapsed_time_minutes,
            official_source_ratio,
        )

        # Generate next iteration focus if continuing
        next_iteration_focus = []
        estimated_iterations_remaining = 0

        if should_continue:
            next_iteration_focus = self._determine_next_iteration_focus(
                gap_analysis, coverage_metrics
            )
            estimated_iterations_remaining = self._estimate_iterations_remaining(
                gap_analysis, coverage_metrics, criteria
            )

        # Calculate confidence in assessment
        confidence = self._calculate_assessment_confidence(
            gap_analysis, coverage_metrics, research_quality_score
        )

        assessment_result = CoverageAssessmentResult(
            assessment_id=f"assessment_{gap_analysis.concept_id}_{datetime.utcnow().strftime('%H%M%S')}",
            concept_id=gap_analysis.concept_id,
            coverage_metrics=coverage_metrics,
            should_continue=should_continue,
            stop_reason=stop_reason,
            next_iteration_focus=next_iteration_focus,
            estimated_iterations_remaining=estimated_iterations_remaining,
            confidence_in_assessment=confidence,
        )

        logger.info(
            f"Coverage assessment complete: should_continue={should_continue}, "
            f"reason={stop_reason}"
        )

        return assessment_result

    async def _calculate_detailed_coverage_metrics(
        self,
        gap_analysis: GapAnalysisResult,
        research_quality_score: float,
        official_source_ratio: float,
    ) -> DetailedCoverageMetrics:
        """Calculate detailed coverage metrics."""
        # Basic coverage metrics
        coverage_metrics = DetailedCoverageMetrics(
            overall_coverage=gap_analysis.coverage_percentage,
            domain_coverage=gap_analysis.domain_completeness,
            research_quality_score=research_quality_score,
        )

        # Calculate specific coverage areas
        coverage_metrics.technical_requirements_coverage = (
            gap_analysis.domain_completeness.get("technical_requirements", 0.0)
        )
        coverage_metrics.business_model_coverage = gap_analysis.domain_completeness.get(
            "business_model", 0.0
        )
        coverage_metrics.integration_coverage = gap_analysis.domain_completeness.get(
            "integration", 0.0
        )
        coverage_metrics.validation_coverage = gap_analysis.domain_completeness.get(
            "validation", 0.0
        )
        coverage_metrics.user_experience_coverage = (
            gap_analysis.domain_completeness.get("user_experience", 0.0)
        )

        # Calculate gap statistics by priority
        coverage_metrics.gaps_by_priority = self._count_gaps_by_priority(
            gap_analysis.identified_gaps
        )
        coverage_metrics.filled_gaps_by_priority = self._count_filled_gaps_by_priority(
            gap_analysis.identified_gaps
        )

        # Identify bottleneck areas
        coverage_metrics.bottleneck_areas = self._identify_bottleneck_areas(
            gap_analysis
        )

        # Calculate efficiency metrics
        coverage_metrics.research_efficiency_score = (
            self._calculate_research_efficiency(gap_analysis, research_quality_score)
        )

        return coverage_metrics

    def _evaluate_quality_gates(
        self, gap_analysis: GapAnalysisResult, coverage_metrics: DetailedCoverageMetrics
    ) -> List[CoverageGate]:
        """Evaluate all quality gates against current coverage."""
        updated_gates = []

        for gate in self._quality_gates:
            updated_gate = CoverageGate(**gate.dict())

            # Calculate score based on gate type
            if gate.gate_name == "technical_completeness":
                updated_gate.current_score = (
                    coverage_metrics.technical_requirements_coverage
                )
            elif gate.gate_name == "business_model_clarity":
                updated_gate.current_score = coverage_metrics.business_model_coverage
            elif gate.gate_name == "user_experience_definition":
                updated_gate.current_score = coverage_metrics.user_experience_coverage
            elif gate.gate_name == "integration_requirements":
                updated_gate.current_score = coverage_metrics.integration_coverage
            elif gate.gate_name == "validation_strategy":
                updated_gate.current_score = coverage_metrics.validation_coverage
            else:
                # Default to overall coverage
                updated_gate.current_score = coverage_metrics.overall_coverage

            # Determine if gate passed
            updated_gate.passed = updated_gate.current_score >= updated_gate.threshold

            updated_gates.append(updated_gate)

        return updated_gates

    def _evaluate_stopping_criteria(
        self,
        gap_analysis: GapAnalysisResult,
        coverage_metrics: DetailedCoverageMetrics,
        criteria: StoppingCriteria,
        iteration_count: int,
        elapsed_time_minutes: float,
        official_source_ratio: float,
    ) -> tuple[bool, Optional[str]]:
        """Evaluate stopping criteria and determine if research should continue.

        Returns:
            Tuple of (should_continue, stop_reason)
        """
        # Check maximum iterations
        if iteration_count >= criteria.maximum_iterations:
            return False, f"Maximum iterations reached ({criteria.maximum_iterations})"

        # Check maximum time
        if elapsed_time_minutes >= criteria.maximum_time_minutes:
            return (
                False,
                f"Maximum time limit reached ({criteria.maximum_time_minutes} minutes)",
            )

        # Check overall coverage
        if gap_analysis.coverage_percentage < criteria.minimum_overall_coverage:
            return True, None

        # Check domain-specific coverage
        for domain, coverage in gap_analysis.domain_completeness.items():
            if coverage < criteria.minimum_domain_coverage:
                return True, None

        # Check critical gaps
        critical_gaps = [
            g for g in gap_analysis.identified_gaps if g.priority == "critical"
        ]
        if critical_gaps:
            filled_critical = len([g for g in critical_gaps if g.filled])
            critical_fill_rate = (filled_critical / len(critical_gaps)) * 100
            if critical_fill_rate < criteria.minimum_critical_gaps_filled:
                return True, None

        # Check high priority gaps
        high_priority_gaps = [
            g for g in gap_analysis.identified_gaps if g.priority == "high"
        ]
        if high_priority_gaps:
            filled_high = len([g for g in high_priority_gaps if g.filled])
            high_fill_rate = (filled_high / len(high_priority_gaps)) * 100
            if high_fill_rate < criteria.minimum_high_priority_gaps_filled:
                return True, None

        # Check required quality gates
        for gate in coverage_metrics.quality_gates:
            if gate.gate_name in criteria.required_quality_gates:
                if not gate.passed:
                    return True, None

        # Check official source ratio
        if official_source_ratio < criteria.minimum_official_source_ratio:
            return True, None

        # All criteria satisfied
        return False, "All stopping criteria satisfied - research complete"

    def _determine_next_iteration_focus(
        self, gap_analysis: GapAnalysisResult, coverage_metrics: DetailedCoverageMetrics
    ) -> List[str]:
        """Determine focus areas for next iteration."""
        focus_areas = []

        # Priority 1: Critical gaps
        critical_gaps = [
            g
            for g in gap_analysis.identified_gaps
            if g.priority == "critical" and not g.filled
        ]
        if critical_gaps:
            focus_areas.extend([g.category for g in critical_gaps[:2]])

        # Priority 2: Failed quality gates
        failed_gates = [
            g
            for g in coverage_metrics.quality_gates
            if not g.passed and g.required_for_completion
        ]
        if failed_gates:
            if "technical_completeness" in [g.gate_name for g in failed_gates]:
                focus_areas.append("technical_requirements")
            if "business_model_clarity" in [g.gate_name for g in failed_gates]:
                focus_areas.append("business_model")

        # Priority 3: Bottleneck areas
        focus_areas.extend(coverage_metrics.bottleneck_areas[:2])

        # Remove duplicates and limit to top 3
        unique_focus_areas = []
        for area in focus_areas:
            if area not in unique_focus_areas:
                unique_focus_areas.append(area)

        return unique_focus_areas[:3]

    def _estimate_iterations_remaining(
        self,
        gap_analysis: GapAnalysisResult,
        coverage_metrics: DetailedCoverageMetrics,
        criteria: StoppingCriteria,
    ) -> int:
        """Estimate number of iterations remaining to meet criteria."""
        # Simple heuristic based on coverage gaps
        coverage_gap = (
            criteria.minimum_overall_coverage - gap_analysis.coverage_percentage
        )

        if coverage_gap <= 0:
            return 0

        # Assume each iteration can improve coverage by 10-20%
        avg_improvement_per_iteration = 15.0
        estimated_iterations = max(1, int(coverage_gap / avg_improvement_per_iteration))

        # Cap at maximum allowed iterations
        return min(estimated_iterations, criteria.maximum_iterations)

    def _calculate_assessment_confidence(
        self,
        gap_analysis: GapAnalysisResult,
        coverage_metrics: DetailedCoverageMetrics,
        research_quality_score: float,
    ) -> float:
        """Calculate confidence in the coverage assessment."""
        confidence_factors = []

        # Factor 1: Research quality
        confidence_factors.append(research_quality_score / 10.0)

        # Factor 2: Number of gaps analyzed
        gap_count_factor = min(len(gap_analysis.identified_gaps) / 10.0, 1.0)
        confidence_factors.append(gap_count_factor)

        # Factor 3: Coverage consistency across domains
        domain_coverages = list(gap_analysis.domain_completeness.values())
        if domain_coverages:
            coverage_variance = sum(
                abs(c - gap_analysis.coverage_percentage) for c in domain_coverages
            ) / len(domain_coverages)
            consistency_factor = max(0, 1.0 - (coverage_variance / 50.0))
            confidence_factors.append(consistency_factor)

        # Factor 4: Quality gate status
        passed_gates = len([g for g in coverage_metrics.quality_gates if g.passed])
        total_gates = len(coverage_metrics.quality_gates)
        gate_factor = passed_gates / total_gates if total_gates > 0 else 1.0
        confidence_factors.append(gate_factor)

        # Calculate weighted average
        return sum(confidence_factors) / len(confidence_factors)

    def _count_gaps_by_priority(self, gaps: List[KnowledgeGap]) -> Dict[str, int]:
        """Count gaps by priority level."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for gap in gaps:
            counts[gap.priority] = counts.get(gap.priority, 0) + 1
        return counts

    def _count_filled_gaps_by_priority(
        self, gaps: List[KnowledgeGap]
    ) -> Dict[str, int]:
        """Count filled gaps by priority level."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for gap in gaps:
            if gap.filled:
                counts[gap.priority] = counts.get(gap.priority, 0) + 1
        return counts

    def _identify_bottleneck_areas(self, gap_analysis: GapAnalysisResult) -> List[str]:
        """Identify areas with lowest coverage that are blocking completion."""
        # Sort domain completeness by coverage percentage
        sorted_areas = sorted(
            gap_analysis.domain_completeness.items(), key=lambda x: x[1]
        )

        # Return bottom 3 areas
        return [area for area, _ in sorted_areas[:3]]

    def _calculate_research_efficiency(
        self, gap_analysis: GapAnalysisResult, research_quality_score: float
    ) -> float:
        """Calculate research efficiency score."""
        # Base score on coverage achieved vs gaps identified
        if len(gap_analysis.identified_gaps) == 0:
            return 10.0  # Perfect if no gaps

        filled_gaps = len([g for g in gap_analysis.identified_gaps if g.filled])
        fill_rate = filled_gaps / len(gap_analysis.identified_gaps)

        # Combine with research quality
        efficiency = (fill_rate * 0.7 + (research_quality_score / 10.0) * 0.3) * 10.0

        return min(efficiency, 10.0)

    async def get_coverage_summary(self, concept_id: str) -> Optional[Dict]:
        """Get a summary of coverage status for a concept.

        Args:
            concept_id: Concept ID to get coverage summary for

        Returns:
            Coverage summary or None if not found
        """
        # This would typically query a database or cache
        # For now, return a placeholder summary
        return {
            "concept_id": concept_id,
            "overall_coverage": 0.0,
            "quality_gates_passed": 0,
            "total_quality_gates": len(self._quality_gates),
            "bottleneck_areas": [],
            "estimated_iterations_remaining": 0,
            "ready_for_completion": False,
        }
