"""Research quality assessment service for evaluating research source quality."""

import logging
from typing import Dict, List, Optional

from ..models.research_iteration import ResearchSource, ResearchQuery
from ..services.research_service import SearchResult

logger = logging.getLogger(__name__)


class ResearchQualityAssessment:
    """Assessment result for research quality."""

    def __init__(
        self,
        overall_quality_score: float,
        official_source_ratio: float,
        source_diversity_score: float,
        relevance_score: float,
        freshness_score: float,
        credibility_score: float,
        quality_breakdown: Dict[str, float],
        recommendations: List[str],
    ):
        self.overall_quality_score = overall_quality_score
        self.official_source_ratio = official_source_ratio
        self.source_diversity_score = source_diversity_score
        self.relevance_score = relevance_score
        self.freshness_score = freshness_score
        self.credibility_score = credibility_score
        self.quality_breakdown = quality_breakdown
        self.recommendations = recommendations


class ResearchQualityAssessor:
    """Service for assessing the quality of research sources and processes."""

    def __init__(self):
        """Initialize the research quality assessor."""
        # Official documentation domains (ordered by priority)
        self.official_docs_domains = [
            "docs.python.org",
            "flask.palletsprojects.com",
            "pydantic-docs.helpmanual.io",
            "docs.aws.amazon.com",
            "cloud.google.com",
            "docs.microsoft.com",
            "kubernetes.io",
            "docker.com",
            "developer.mozilla.org",
            "reactjs.org",
            "vuejs.org",
            "angular.io",
            "nodejs.org",
            "postgresql.org",
            "redis.io",
            "mongodb.com/docs",
            "stripe.com/docs",
            "github.com",  # For official repositories
        ]

        # High-quality community domains
        self.quality_community_domains = [
            "stackoverflow.com",
            "dev.to",
            "medium.com",
            "realpython.com",
            "digitalocean.com",
            "atlassian.com",
            "auth0.com/blog",
            "twilio.com/docs",
        ]

        # Low-quality or unreliable domains
        self.low_quality_domains = [
            "w3schools.com",  # Often outdated or oversimplified
            "tutorialspoint.com",
            "geeksforgeeks.org",  # Sometimes contains errors
        ]

        # Quality indicators in content
        self.quality_indicators = {
            "positive": [
                "official documentation",
                "best practices",
                "recommended approach",
                "production-ready",
                "security considerations",
                "performance",
                "scalability",
                "maintainability",
                "testing",
                "validation",
                "error handling",
                "monitoring",
                "logging",
            ],
            "negative": [
                "quick hack",
                "temporary solution",
                "not recommended",
                "deprecated",
                "experimental",
                "untested",
                "proof of concept",
                "toy example",
                "simplified version",
            ],
        }

    async def assess_source_quality(
        self, sources: List[SearchResult], query_context: Optional[str] = None
    ) -> ResearchQualityAssessment:
        """Assess the quality of research sources.

        Args:
            sources: List of search results to assess
            query_context: Context of what was being researched

        Returns:
            Research quality assessment with scores and recommendations
        """
        if not sources:
            return ResearchQualityAssessment(
                overall_quality_score=0.0,
                official_source_ratio=0.0,
                source_diversity_score=0.0,
                relevance_score=0.0,
                freshness_score=0.0,
                credibility_score=0.0,
                quality_breakdown={},
                recommendations=["No sources found - research was not conducted"],
            )

        logger.info(f"Assessing quality of {len(sources)} research sources")

        # Calculate individual quality metrics
        official_ratio = self._calculate_official_source_ratio(sources)
        diversity_score = self._calculate_source_diversity_score(sources)
        relevance_score = self._calculate_relevance_score(sources, query_context)
        freshness_score = self._calculate_freshness_score(sources)
        credibility_score = self._calculate_credibility_score(sources)

        # Calculate overall quality score (weighted average)
        weights = {
            "official_ratio": 0.3,
            "diversity": 0.15,
            "relevance": 0.25,
            "freshness": 0.15,
            "credibility": 0.15,
        }

        overall_score = (
            official_ratio * weights["official_ratio"]
            + diversity_score * weights["diversity"]
            + relevance_score * weights["relevance"]
            + freshness_score * weights["freshness"]
            + credibility_score * weights["credibility"]
        ) * 10.0  # Scale to 0-10

        # Generate quality breakdown
        quality_breakdown = {
            "official_sources": official_ratio * 10.0,
            "source_diversity": diversity_score * 10.0,
            "content_relevance": relevance_score * 10.0,
            "information_freshness": freshness_score * 10.0,
            "source_credibility": credibility_score * 10.0,
        }

        # Generate recommendations
        recommendations = self._generate_quality_recommendations(
            sources,
            official_ratio,
            diversity_score,
            relevance_score,
            freshness_score,
            credibility_score,
        )

        assessment = ResearchQualityAssessment(
            overall_quality_score=overall_score,
            official_source_ratio=official_ratio,
            source_diversity_score=diversity_score * 10.0,
            relevance_score=relevance_score * 10.0,
            freshness_score=freshness_score * 10.0,
            credibility_score=credibility_score * 10.0,
            quality_breakdown=quality_breakdown,
            recommendations=recommendations,
        )

        logger.info(
            f"Research quality assessment complete: "
            f"overall_score={overall_score:.1f}, "
            f"official_ratio={official_ratio:.2f}"
        )

        return assessment

    def _calculate_official_source_ratio(self, sources: List[SearchResult]) -> float:
        """Calculate ratio of official documentation sources.

        CONSTRAINT: Prioritize official vendor documentation sources.
        """
        if not sources:
            return 0.0

        official_count = 0
        for source in sources:
            if self._is_official_documentation(source.domain):
                official_count += 1
            elif source.domain == "github.com" and self._is_official_github_repo(
                source.url, source.title
            ):
                official_count += 1

        return official_count / len(sources)

    def _calculate_source_diversity_score(self, sources: List[SearchResult]) -> float:
        """Calculate diversity score based on domain variety and content types."""
        if not sources:
            return 0.0

        # Count unique domains
        unique_domains = set(source.domain for source in sources)
        domain_diversity = min(len(unique_domains) / len(sources), 1.0)

        # Count content types
        content_types = set()
        for source in sources:
            if "docs" in source.domain or "documentation" in source.title.lower():
                content_types.add("documentation")
            elif "github.com" in source.domain:
                content_types.add("code_repository")
            elif "stackoverflow.com" in source.domain:
                content_types.add("community_qa")
            elif "blog" in source.url or "medium.com" in source.domain:
                content_types.add("blog_article")
            else:
                content_types.add("general_web")

        type_diversity = min(
            len(content_types) / 3.0, 1.0
        )  # Expect up to 3 different types

        # Combined diversity score
        return domain_diversity * 0.6 + type_diversity * 0.4

    def _calculate_relevance_score(
        self, sources: List[SearchResult], query_context: Optional[str]
    ) -> float:
        """Calculate relevance score based on content analysis."""
        if not sources:
            return 0.0

        total_relevance = 0.0

        for source in sources:
            relevance = source.relevance_score / 10.0  # Normalize to 0-1

            # Boost for content quality indicators
            content = (source.title + " " + source.snippet).lower()

            positive_indicators = sum(
                1
                for indicator in self.quality_indicators["positive"]
                if indicator in content
            )
            negative_indicators = sum(
                1
                for indicator in self.quality_indicators["negative"]
                if indicator in content
            )

            # Adjust relevance based on quality indicators
            indicator_adjustment = (positive_indicators * 0.1) - (
                negative_indicators * 0.15
            )
            relevance = max(0.0, min(1.0, relevance + indicator_adjustment))

            total_relevance += relevance

        return total_relevance / len(sources)

    def _calculate_freshness_score(self, sources: List[SearchResult]) -> float:
        """Calculate freshness score (placeholder - would need publication dates)."""
        # In a real implementation, this would analyze publication dates
        # For now, we'll use domain-based heuristics

        freshness_scores = []

        for source in sources:
            if self._is_official_documentation(source.domain):
                # Official docs are usually well-maintained
                freshness_scores.append(0.9)
            elif "github.com" in source.domain:
                # GitHub repos can vary, but are often current
                freshness_scores.append(0.8)
            elif source.domain in self.quality_community_domains:
                # Quality community sites are usually current
                freshness_scores.append(0.7)
            else:
                # Other sources may be less current
                freshness_scores.append(0.5)

        return (
            sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.0
        )

    def _calculate_credibility_score(self, sources: List[SearchResult]) -> float:
        """Calculate credibility score based on source reputation."""
        credibility_scores = []

        for source in sources:
            if self._is_official_documentation(source.domain):
                # Official documentation is highly credible
                credibility_scores.append(1.0)
            elif source.domain in self.quality_community_domains:
                # Known quality community sites
                credibility_scores.append(0.8)
            elif source.domain in self.low_quality_domains:
                # Known low-quality sites
                credibility_scores.append(0.3)
            elif "github.com" in source.domain:
                # GitHub credibility depends on repository
                if self._is_official_github_repo(source.url, source.title):
                    credibility_scores.append(0.9)
                else:
                    credibility_scores.append(0.6)
            else:
                # Unknown sources get neutral score
                credibility_scores.append(0.5)

        return (
            sum(credibility_scores) / len(credibility_scores)
            if credibility_scores
            else 0.0
        )

    def _is_official_documentation(self, domain: str) -> bool:
        """Check if domain is official documentation."""
        return domain in self.official_docs_domains

    def _is_official_github_repo(self, url: str, title: str) -> bool:
        """Check if GitHub repository is official."""
        # Simple heuristics for official repos
        official_indicators = [
            "official",
            "docs",
            "documentation",
            "guide",
            "flask",
            "python",
            "django",
            "react",
            "vue",
            "angular",
        ]

        url_lower = url.lower()
        title_lower = title.lower()

        return any(
            indicator in url_lower or indicator in title_lower
            for indicator in official_indicators
        )

    def _generate_quality_recommendations(
        self,
        sources: List[SearchResult],
        official_ratio: float,
        diversity_score: float,
        relevance_score: float,
        freshness_score: float,
        credibility_score: float,
    ) -> List[str]:
        """Generate recommendations for improving research quality."""
        recommendations = []

        # Official source ratio recommendations
        if official_ratio < 0.5:
            recommendations.append(
                "Increase official documentation sources - currently only "
                f"{official_ratio:.0%} of sources are official docs"
            )
        elif official_ratio > 0.9:
            recommendations.append(
                "Good official source coverage, consider adding community perspectives"
            )

        # Diversity recommendations
        if diversity_score < 0.5:
            recommendations.append(
                "Increase source diversity - research from more varied domains and content types"
            )

        # Relevance recommendations
        if relevance_score < 0.6:
            recommendations.append(
                "Improve search query specificity to find more relevant sources"
            )

        # Credibility recommendations
        if credibility_score < 0.7:
            recommendations.append(
                "Focus on higher-credibility sources - avoid low-quality tutorial sites"
            )

        # Domain-specific recommendations
        domains = [source.domain for source in sources]
        if any(domain in self.low_quality_domains for domain in domains):
            recommendations.append(
                "Avoid low-quality sources like w3schools or tutorialspoint - "
                "prefer official documentation"
            )

        # Source count recommendations
        if len(sources) < 3:
            recommendations.append(
                f"Insufficient sources ({len(sources)}) - aim for 5-10 sources per research query"
            )
        elif len(sources) > 15:
            recommendations.append(
                f"Too many sources ({len(sources)}) - focus on top 10 highest quality results"
            )

        if not recommendations:
            recommendations.append(
                "Research quality is good - maintain current approach"
            )

        return recommendations

    async def assess_research_iteration_quality(
        self,
        queries: List[ResearchQuery],
        sources: List[ResearchSource],
        gaps_targeted: List[str],
        iteration_time_minutes: float,
    ) -> Dict[str, float]:
        """Assess quality of an entire research iteration.

        Args:
            queries: Research queries executed
            sources: Sources found during research
            gaps_targeted: Knowledge gaps this iteration targeted
            iteration_time_minutes: Time spent on iteration

        Returns:
            Dictionary of quality metrics for the iteration
        """
        # Convert ResearchSource to SearchResult for compatibility
        search_results = []
        for source in sources:
            search_results.append(
                SearchResult(
                    title=source.title,
                    url=source.url,
                    snippet=source.snippet,
                    domain=source.domain,
                    relevance_score=source.relevance_score,
                    is_official_docs=source.is_official_docs,
                    content_type=source.content_type,
                )
            )

        # Assess source quality
        source_assessment = await self.assess_source_quality(search_results)

        # Additional iteration-specific metrics
        query_quality_score = self._assess_query_quality(queries, gaps_targeted)
        efficiency_score = self._assess_research_efficiency(
            len(queries), len(sources), iteration_time_minutes
        )

        return {
            "source_quality_score": source_assessment.overall_quality_score,
            "official_source_ratio": source_assessment.official_source_ratio,
            "query_quality_score": query_quality_score,
            "research_efficiency_score": efficiency_score,
            "source_diversity_score": source_assessment.source_diversity_score,
            "overall_iteration_quality": (
                source_assessment.overall_quality_score * 0.4
                + query_quality_score * 0.3
                + efficiency_score * 0.3
            ),
        }

    def _assess_query_quality(
        self, queries: List[ResearchQuery], gaps_targeted: List[str]
    ) -> float:
        """Assess the quality of research queries."""
        if not queries:
            return 0.0

        query_scores = []

        for query in queries:
            score = 5.0  # Base score

            # Reward specific queries
            if len(query.query_text.split()) >= 3:
                score += 1.0

            # Reward domain-specific queries
            if any(gap in query.query_text.lower() for gap in gaps_targeted):
                score += 1.0

            # Reward official source preference
            if query.official_sources_preference:
                score += 1.0

            # Penalize overly broad queries
            if len(query.query_text.split()) < 2:
                score -= 1.0

            query_scores.append(min(score, 10.0))

        return sum(query_scores) / len(query_scores)

    def _assess_research_efficiency(
        self, query_count: int, source_count: int, time_minutes: float
    ) -> float:
        """Assess research process efficiency."""
        # Base efficiency score
        efficiency = 5.0

        # Reward good source-to-query ratio
        if query_count > 0:
            source_per_query = source_count / query_count
            if 2 <= source_per_query <= 8:  # Sweet spot
                efficiency += 2.0
            elif source_per_query < 1:
                efficiency -= 1.0

        # Time efficiency
        if time_minutes > 0:
            sources_per_minute = source_count / time_minutes
            if sources_per_minute >= 1.0:
                efficiency += 1.0
            elif sources_per_minute < 0.5:
                efficiency -= 1.0

        # Penalize too many or too few sources
        if source_count < 3:
            efficiency -= 1.0
        elif source_count > 20:
            efficiency -= 0.5

        return min(efficiency, 10.0)
