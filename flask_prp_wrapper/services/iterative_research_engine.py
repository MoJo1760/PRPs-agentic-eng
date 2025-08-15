"""Iterative research engine that continues researching until stopping criteria are met."""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Tuple

from ..models.business_concept import BusinessConceptRequest
from ..models.gap_analysis import (
    GapAnalysisResult,
    ResearchIteration,
    CoverageMetrics,
    IterativeResearchResult,
)
from ..models.research_iteration import DetailedResearchIteration
from ..models.coverage_metrics import CoverageAssessmentResult, StoppingCriteria
from ..services.gap_analysis_service import GapAnalysisService
from ..services.coverage_validator import CoverageValidator
from ..services.research_quality_assessor import ResearchQualityAssessor
from ..services.research_service import ResearchService, ResearchContext
from ..services.questioning_engine import QuestioningEngine
from ..models.questionnaire import QuestionnaireGenerationRequest

logger = logging.getLogger(__name__)


class IterativeResearchEngine:
    """Main orchestration service for iterative research with automatic stopping."""

    def __init__(
        self,
        gap_analysis_service: Optional[GapAnalysisService] = None,
        coverage_validator: Optional[CoverageValidator] = None,
        research_quality_assessor: Optional[ResearchQualityAssessor] = None,
        research_service: Optional[ResearchService] = None,
        questioning_engine: Optional[QuestioningEngine] = None,
        max_iterations: int = 5,
        max_research_time_minutes: int = 30,
    ):
        """Initialize the iterative research engine.

        Args:
            gap_analysis_service: Service for analyzing knowledge gaps
            coverage_validator: Service for validating requirement coverage
            research_quality_assessor: Service for assessing research quality
            research_service: Service for conducting research
            questioning_engine: Service for generating targeted questions
            max_iterations: Maximum number of research iterations
            max_research_time_minutes: Maximum total research time in minutes
        """
        self.gap_analysis_service = gap_analysis_service or GapAnalysisService()
        self.coverage_validator = coverage_validator or CoverageValidator()
        self.research_quality_assessor = (
            research_quality_assessor or ResearchQualityAssessor()
        )
        self.research_service = research_service or ResearchService()
        self.questioning_engine = questioning_engine or QuestioningEngine()

        self.max_iterations = max_iterations
        self.max_research_time_minutes = max_research_time_minutes

        # Default stopping criteria
        self.default_stopping_criteria = StoppingCriteria(
            min_overall_coverage=95.0,
            min_domain_coverage=85.0,
            min_research_quality_score=7.0,
            max_iterations=max_iterations,
            max_research_time_minutes=max_research_time_minutes,
        )

    async def conduct_iterative_research(
        self,
        concept: BusinessConceptRequest,
        existing_research: Optional[ResearchContext] = None,
        stopping_criteria: Optional[StoppingCriteria] = None,
        questionnaire_responses: Optional[List] = None,
    ) -> IterativeResearchResult:
        """Conduct iterative research until stopping criteria are met.

        Args:
            concept: Business concept to research
            existing_research: Any existing research context
            stopping_criteria: Custom stopping criteria (uses defaults if None)
            questionnaire_responses: Previous questionnaire responses

        Returns:
            Complete iterative research result with all iterations
        """
        start_time = datetime.utcnow()
        criteria = stopping_criteria or self.default_stopping_criteria
        iterations = []
        current_research = existing_research
        current_responses = questionnaire_responses or []

        logger.info(
            f"Starting iterative research for concept: {concept.title} "
            f"(max_iterations={criteria.max_iterations}, "
            f"target_coverage={criteria.min_overall_coverage}%)"
        )

        for iteration_num in range(1, criteria.max_iterations + 1):
            # Check time limit
            elapsed_time = (datetime.utcnow() - start_time).total_seconds() / 60
            if elapsed_time >= criteria.max_research_time_minutes:
                logger.info(
                    f"Research stopped due to time limit: {elapsed_time:.1f} minutes"
                )
                break

            logger.info(f"Starting research iteration {iteration_num}")

            # Conduct iteration
            try:
                iteration_result = await self._conduct_single_iteration(
                    concept=concept,
                    iteration_number=iteration_num,
                    existing_research=current_research,
                    questionnaire_responses=current_responses,
                    criteria=criteria,
                )

                iterations.append(iteration_result)

                # Update current research context if new information was found
                if (
                    iteration_result.research_context
                    and iteration_result.research_context.research_quality_score
                    > (current_research.research_quality_score if current_research else 0)
                ):
                    current_research = iteration_result.research_context

                # Add any new questionnaire responses
                if iteration_result.generated_questions:
                    current_responses.extend(iteration_result.generated_questions)

                # Check stopping criteria
                should_stop, stop_reason = await self._should_stop_research(
                    iteration_result.coverage_assessment, criteria, iteration_num, elapsed_time
                )

                if should_stop:
                    logger.info(f"Research stopped: {stop_reason}")
                    break

            except Exception as e:
                logger.error(f"Error in research iteration {iteration_num}: {e}")
                # Create failed iteration record
                failed_iteration = DetailedResearchIteration(
                    id=f"iteration_{iteration_num}_{concept.title[:20]}",
                    concept_id=f"concept_{concept.title[:20]}",
                    iteration_number=iteration_num,
                    status="failed",
                    error_message=str(e),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )
                iterations.append(failed_iteration)
                break

        # Calculate final metrics
        final_metrics = await self._calculate_final_metrics(
            concept, current_research, current_responses, iterations
        )

        # Determine success
        success = (
            final_metrics.overall_coverage >= criteria.min_overall_coverage
            and final_metrics.research_quality_score >= criteria.min_research_quality_score
        )

        total_time = (datetime.utcnow() - start_time).total_seconds() / 60

        result = IterativeResearchResult(
            concept_id=f"concept_{concept.title[:20]}",
            iterations=[self._convert_to_basic_iteration(it) for it in iterations],
            final_coverage_metrics=final_metrics,
            total_gaps_identified=sum(
                len(it.gap_analysis_result.identified_gaps)
                for it in iterations
                if hasattr(it, 'gap_analysis_result') and it.gap_analysis_result
            ),
            gaps_filled=sum(
                len([g for g in it.gap_analysis_result.identified_gaps if g.filled])
                for it in iterations
                if hasattr(it, 'gap_analysis_result') and it.gap_analysis_result
            ),
            total_research_time_minutes=total_time,
            official_sources_used=sum(
                it.official_sources_found for it in iterations if hasattr(it, 'official_sources_found')
            ),
            questions_generated=sum(
                len(it.generated_questions) for it in iterations if hasattr(it, 'generated_questions')
            ),
            early_stop_reason=stop_reason if len(iterations) < criteria.max_iterations else None,
            success=success,
            ready_for_prp_generation=success and final_metrics.overall_coverage >= 90.0,
        )

        logger.info(
            f"Iterative research complete: {len(iterations)} iterations, "
            f"{final_metrics.overall_coverage:.1f}% coverage, "
            f"success={success}"
        )

        return result

    async def _conduct_single_iteration(
        self,
        concept: BusinessConceptRequest,
        iteration_number: int,
        existing_research: Optional[ResearchContext],
        questionnaire_responses: List,
        criteria: StoppingCriteria,
    ) -> DetailedResearchIteration:
        """Conduct a single research iteration.

        Args:
            concept: Business concept being researched
            iteration_number: Current iteration number
            existing_research: Research context from previous iterations
            questionnaire_responses: Accumulated questionnaire responses
            criteria: Stopping criteria for validation

        Returns:
            Detailed results of this research iteration
        """
        iteration_start = datetime.utcnow()
        iteration_id = f"iteration_{iteration_number}_{concept.title[:20]}"

        # Step 1: Analyze current gaps
        logger.debug(f"Iteration {iteration_number}: Analyzing gaps")
        gap_analysis = await self.gap_analysis_service.analyze_concept_gaps(
            concept=concept,
            existing_research=existing_research,
            questionnaire_responses=questionnaire_responses,
        )

        # Step 2: Prioritize research areas based on gaps
        priority_areas = gap_analysis.next_research_areas[:3]  # Top 3 priority areas

        # Step 3: Conduct targeted research for high-priority gaps
        research_queries = []
        research_context = existing_research
        official_sources_count = 0

        for area in priority_areas:
            # Generate research queries for this area
            area_queries = await self._generate_research_queries_for_area(
                area, concept, gap_analysis
            )
            research_queries.extend(area_queries)

            # Conduct research if we have a research service
            if area_queries and self.research_service:
                try:
                    area_research = await self.research_service.gather_business_domain_context(
                        domain=concept.domain.value if concept.domain else "general",
                        business_model=concept.business_model.value if concept.business_model else "general",
                        concept_description=f"{concept.description} Focus: {area}",
                    )
                    
                    # Count official sources
                    official_sources_count += len(area_research.official_documentation_links)

                    # Merge with existing research
                    if research_context is None:
                        research_context = area_research
                    else:
                        research_context = await self._merge_research_contexts(
                            research_context, area_research
                        )

                except Exception as e:
                    logger.warning(f"Research failed for area {area}: {e}")

        # Step 4: Generate targeted questions based on gaps
        generated_questions = []
        if gap_analysis.identified_gaps:
            try:
                # Generate questions targeting the highest priority gaps
                high_priority_gaps = [
                    g for g in gap_analysis.identified_gaps
                    if g.priority in ["critical", "high"]
                ][:5]

                if high_priority_gaps:
                    questionnaire_request = QuestionnaireGenerationRequest(
                        concept_id=gap_analysis.concept_id,
                        max_questions=len(high_priority_gaps),
                        focus_areas=[g.category for g in high_priority_gaps],
                        difficulty_level="intermediate",
                    )

                    questions = await self.questioning_engine.generate_questions(
                        questionnaire_request, concept
                    )
                    generated_questions = [q.text for q in questions]

            except Exception as e:
                logger.warning(f"Question generation failed: {e}")

        # Step 5: Assess research quality
        research_quality_score = 0.0
        if research_context:
            try:
                # Create mock SearchResults for quality assessment
                from ..services.research_service import SearchResult
                mock_results = [
                    SearchResult(
                        title=f"Research for {area}",
                        url=link,
                        snippet=f"Content from {area}",
                        domain=link.split('//')[1].split('/')[0] if '//' in link else "unknown",
                        relevance_score=8.0,
                        is_official_docs=any(
                            domain in link for domain in self.research_service.official_docs_domains
                        ),
                        content_type="documentation" if "docs." in link else "webpage",
                    )
                    for area in priority_areas
                    for link in research_context.official_documentation_links[:2]
                ]

                if mock_results:
                    quality_assessment = await self.research_quality_assessor.assess_source_quality(
                        mock_results
                    )
                    research_quality_score = quality_assessment.overall_quality_score

            except Exception as e:
                logger.warning(f"Quality assessment failed: {e}")

        # Step 6: Validate coverage
        coverage_assessment = await self.coverage_validator.validate_coverage(
            gap_analysis, research_quality_score
        )

        # Step 7: Calculate coverage improvement
        coverage_improvement = 0.0
        if iteration_number > 1:
            # In a real implementation, we'd track previous coverage
            coverage_improvement = min(5.0, gap_analysis.coverage_percentage / iteration_number)

        # Create iteration result
        iteration = DetailedResearchIteration(
            id=iteration_id,
            concept_id=gap_analysis.concept_id,
            iteration_number=iteration_number,
            gaps_targeted=[g.id for g in gap_analysis.identified_gaps[:5]],
            detailed_research_queries=research_queries,
            official_sources_found=official_sources_count,
            questions_generated=len(generated_questions),
            coverage_improvement=coverage_improvement,
            official_source_ratio=min(1.0, official_sources_count / max(len(research_queries), 1)),
            started_at=iteration_start,
            completed_at=datetime.utcnow(),
            status="completed",
            gap_analysis_result=gap_analysis,
            research_context=research_context,
            coverage_assessment=coverage_assessment,
            generated_questions=generated_questions,
            research_quality_score=research_quality_score,
        )

        logger.info(
            f"Iteration {iteration_number} completed: "
            f"{len(gap_analysis.identified_gaps)} gaps, "
            f"{gap_analysis.coverage_percentage:.1f}% coverage, "
            f"{official_sources_count} official sources"
        )

        return iteration

    async def _generate_research_queries_for_area(
        self, area: str, concept: BusinessConceptRequest, gap_analysis: GapAnalysisResult
    ) -> List[str]:
        """Generate targeted research queries for a specific area."""
        queries = []
        
        # Base query with official documentation preference
        base_query = f"{area} {concept.domain.value if concept.domain else 'application'} official documentation"
        queries.append(base_query)

        # Add specific queries based on area and gaps
        area_gaps = [g for g in gap_analysis.identified_gaps if g.category == area]
        
        for gap in area_gaps[:2]:  # Top 2 gaps per area
            gap_query = f"{area} {gap.description.replace('Missing or insufficient information about:', '').strip()} best practices"
            queries.append(gap_query)

        # Domain-specific queries
        domain = concept.domain.value if concept.domain else "general"
        domain_query = f"{domain} {area} patterns site:docs.python.org OR site:flask.palletsprojects.com"
        queries.append(domain_query)

        return queries[:3]  # Limit to 3 queries per area

    async def _merge_research_contexts(
        self, context1: ResearchContext, context2: ResearchContext
    ) -> ResearchContext:
        """Merge two research contexts, preferring higher quality information."""
        # Simple merge - in production this would be more sophisticated
        merged_patterns = list(set(context1.technical_patterns + context2.technical_patterns))
        merged_practices = list(set(context1.best_practices + context2.best_practices))
        merged_challenges = list(set(context1.common_challenges + context2.common_challenges))
        merged_technologies = list(set(context1.recommended_technologies + context2.recommended_technologies))
        merged_validation = list(set(context1.validation_approaches + context2.validation_approaches))
        merged_docs = list(set(context1.official_documentation_links + context2.official_documentation_links))
        merged_competitors = list(set(context1.competitor_analysis + context2.competitor_analysis))

        # Use the context with higher quality score as base
        base_context = context1 if context1.research_quality_score >= context2.research_quality_score else context2
        
        return ResearchContext(
            domain_overview=base_context.domain_overview,
            technical_patterns=merged_patterns[:5],  # Keep top 5
            best_practices=merged_practices[:5],
            common_challenges=merged_challenges[:5],
            recommended_technologies=merged_technologies[:5],
            validation_approaches=merged_validation[:3],
            official_documentation_links=merged_docs[:5],
            competitor_analysis=merged_competitors[:3],
            research_timestamp=datetime.utcnow(),
            research_quality_score=max(context1.research_quality_score, context2.research_quality_score),
        )

    async def _should_stop_research(
        self,
        coverage_assessment: CoverageAssessmentResult,
        criteria: StoppingCriteria,
        iteration_num: int,
        elapsed_time_minutes: float,
    ) -> Tuple[bool, str]:
        """Determine if research should stop based on criteria."""
        
        # Check maximum iterations
        if iteration_num >= criteria.max_iterations:
            return True, f"Maximum iterations reached ({criteria.max_iterations})"

        # Check time limit
        if elapsed_time_minutes >= criteria.max_research_time_minutes:
            return True, f"Time limit reached ({elapsed_time_minutes:.1f} minutes)"

        # Check coverage thresholds
        if coverage_assessment.coverage_metrics.overall_coverage >= criteria.min_overall_coverage:
            domain_coverage_ok = all(
                coverage >= criteria.min_domain_coverage
                for coverage in coverage_assessment.coverage_metrics.domain_coverage.values()
            )
            if domain_coverage_ok:
                return True, f"Coverage targets met ({coverage_assessment.coverage_metrics.overall_coverage:.1f}%)"

        # Check research quality
        if coverage_assessment.coverage_metrics.research_quality_score >= criteria.min_research_quality_score:
            if coverage_assessment.coverage_metrics.overall_coverage >= criteria.min_overall_coverage - 5.0:  # Allow 5% tolerance
                return True, f"Quality and coverage targets met (quality: {coverage_assessment.coverage_metrics.research_quality_score:.1f})"

        # Continue research
        return False, ""

    async def _calculate_final_metrics(
        self,
        concept: BusinessConceptRequest,
        final_research: Optional[ResearchContext],
        responses: List,
        iterations: List,
    ) -> CoverageMetrics:
        """Calculate final coverage metrics for the research process."""
        
        # Get the latest gap analysis from iterations
        latest_gap_analysis = None
        for iteration in reversed(iterations):
            if hasattr(iteration, 'gap_analysis_result') and iteration.gap_analysis_result:
                latest_gap_analysis = iteration.gap_analysis_result
                break

        overall_coverage = latest_gap_analysis.coverage_percentage if latest_gap_analysis else 0.0
        domain_completeness = latest_gap_analysis.domain_completeness if latest_gap_analysis else {}

        # Calculate research quality score
        research_quality = final_research.research_quality_score if final_research else 0.0

        # Determine if stopping criteria are met
        stopping_criteria_met = (
            overall_coverage >= self.default_stopping_criteria.min_overall_coverage
            and research_quality >= self.default_stopping_criteria.min_research_quality_score
        )

        # Generate recommendations
        recommendations = []
        if overall_coverage < 95.0:
            recommendations.append("Continue research to improve coverage")
        if research_quality < 7.0:
            recommendations.append("Focus on official documentation sources")
        if not recommendations:
            recommendations.append("Ready for PRP generation")

        # Quality gates
        quality_gates = {
            "coverage_threshold": overall_coverage >= 95.0,
            "quality_threshold": research_quality >= 7.0,
            "official_sources": final_research and len(final_research.official_documentation_links) >= 3,
            "technical_patterns": final_research and len(final_research.technical_patterns) >= 3,
        }

        return CoverageMetrics(
            overall_coverage=overall_coverage,
            domain_coverage=domain_completeness,
            technical_requirements_coverage=domain_completeness.get("technical_requirements", 0.0),
            business_model_coverage=domain_completeness.get("business_model", 0.0),
            integration_coverage=domain_completeness.get("integration", 0.0),
            validation_coverage=domain_completeness.get("validation", 0.0),
            user_experience_coverage=domain_completeness.get("user_experience", 0.0),
            stopping_criteria_met=stopping_criteria_met,
            recommended_next_steps=recommendations,
            quality_gates_passed=quality_gates,
            research_quality_score=research_quality,
        )

    def _convert_to_basic_iteration(self, detailed_iteration: DetailedResearchIteration) -> ResearchIteration:
        """Convert detailed iteration to basic iteration for final result."""
        return ResearchIteration(
            id=detailed_iteration.id,
            concept_id=detailed_iteration.concept_id,
            iteration_number=detailed_iteration.iteration_number,
            gaps_targeted=detailed_iteration.gaps_targeted,
            research_queries=detailed_iteration.detailed_research_queries[:5],  # Limit for basic version
            official_sources_found=detailed_iteration.official_sources_found,
            questions_generated=detailed_iteration.questions_generated,
            coverage_improvement=detailed_iteration.coverage_improvement,
            official_source_ratio=detailed_iteration.official_source_ratio,
            started_at=detailed_iteration.started_at,
            completed_at=detailed_iteration.completed_at,
            status=detailed_iteration.status,
            error_message=detailed_iteration.error_message,
        )

    async def get_research_progress(self, concept_id: str) -> Optional[Dict]:
        """Get current research progress for a concept.
        
        This would typically query a database for stored research progress.
        For now, returns a placeholder structure.
        """
        # In a real implementation, this would query persistent storage
        return {
            "concept_id": concept_id,
            "status": "research_in_progress",
            "current_iteration": 1,
            "coverage_percentage": 0.0,
            "gaps_identified": 0,
            "gaps_filled": 0,
            "estimated_completion": "unknown"
        }

    async def resume_research(
        self, 
        concept_id: str, 
        last_iteration: int,
        existing_result: IterativeResearchResult
    ) -> IterativeResearchResult:
        """Resume research from a previous iteration.
        
        This would be used to continue research that was interrupted.
        """
        # In a real implementation, this would load the previous state
        # and continue from where it left off
        logger.info(f"Resume functionality not fully implemented. Would resume research for {concept_id} from iteration {last_iteration}")
        return existing_result