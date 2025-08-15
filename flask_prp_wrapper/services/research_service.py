"""Research service with preference for official vendor documentation."""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..models.gap_analysis import KnowledgeGap

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Individual search result."""

    title: str
    url: str
    snippet: str
    domain: str
    relevance_score: float
    is_official_docs: bool = False
    content_type: str = "webpage"  # webpage, documentation, github, stackoverflow, etc.


@dataclass
class ResearchContext:
    """Comprehensive research context for PRP generation."""

    domain_overview: str
    technical_patterns: List[str]
    best_practices: List[str]
    common_challenges: List[str]
    recommended_technologies: List[str]
    validation_approaches: List[str]
    official_documentation_links: List[str]
    competitor_analysis: List[str]
    research_timestamp: datetime
    research_quality_score: float


class ResearchService:
    """Automated research service with official documentation preference."""

    def __init__(self, web_search_client=None, cache_ttl: int = 3600):
        """Initialize research service.

        Args:
            web_search_client: Web search API client
            cache_ttl: Cache time-to-live in seconds
        """
        self.web_search_client = web_search_client
        self.cache_ttl = cache_ttl
        self._research_cache: Dict[str, Tuple[ResearchContext, datetime]] = {}

        # Official documentation domains (prioritized in research)
        self.official_docs_domains = [
            "docs.python.org",
            "flask.palletsprojects.com",
            "pydantic-docs.helpmanual.io",
            "docs.aws.amazon.com",
            "cloud.google.com",
            "docs.microsoft.com",
            "kubernetes.io",
            "docker.com",
            "github.com",  # For official repositories
            "developer.mozilla.org",
            "reactjs.org",
            "vuejs.org",
            "angular.io",
            "nodejs.org",
            "postgresql.org",
            "redis.io",
            "mongodb.com/docs",
        ]

        # Technical pattern queries for different domains
        self.domain_query_templates = {
            "saas": [
                "SaaS architecture patterns multi-tenancy site:docs.python.org OR site:flask.palletsprojects.com",
                "subscription billing integration patterns official documentation",
                "user authentication authorization SaaS best practices",
                "API rate limiting SaaS applications",
            ],
            "e_commerce": [
                "e-commerce payment processing integration patterns site:docs.aws.amazon.com",
                "inventory management system architecture patterns",
                "order processing workflow e-commerce",
                "shopping cart session management best practices",
            ],
            "mobile_app": [
                "mobile app backend API design patterns",
                "push notifications service implementation",
                "offline data synchronization mobile apps",
                "mobile app authentication patterns",
            ],
            "fintech": [
                "financial data security patterns site:docs.aws.amazon.com",
                "payment processing API integration patterns",
                "PCI compliance implementation patterns",
                "financial transaction audit logging",
            ],
            "healthcare": [
                "HIPAA compliant application architecture",
                "healthcare data encryption patterns",
                "medical record API security patterns",
                "healthcare application validation requirements",
            ],
        }

    async def gather_business_domain_context(
        self, domain: str, business_model: str, concept_description: str
    ) -> ResearchContext:
        """Gather comprehensive research context for business domain.

        CONSTRAINT: PREFER official vendor documentation sources over third-party content.
        Priority order: Official docs > GitHub repos > Stack Overflow > Blog posts
        """
        cache_key = f"{domain}_{business_model}_{hash(concept_description)}"

        # Check cache first
        if cache_key in self._research_cache:
            cached_context, timestamp = self._research_cache[cache_key]
            if datetime.utcnow() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.info(f"Using cached research context for {domain}")
                return cached_context

        logger.info(
            f"Conducting research for domain: {domain}, business model: {business_model}"
        )

        # Parallel research tasks with official documentation preference
        tasks = [
            self._research_domain_overview(domain, concept_description),
            self._research_technical_patterns(domain, business_model),
            self._research_best_practices(domain),
            self._research_validation_approaches(domain),
            self._research_competitors(domain, concept_description),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        domain_overview = (
            results[0]
            if not isinstance(results[0], Exception)
            else f"Overview for {domain} domain"
        )
        technical_patterns = results[1] if not isinstance(results[1], Exception) else []
        best_practices = results[2] if not isinstance(results[2], Exception) else []
        validation_approaches = (
            results[3] if not isinstance(results[3], Exception) else []
        )
        competitor_analysis = (
            results[4] if not isinstance(results[4], Exception) else []
        )

        # Generate recommended technologies based on research
        recommended_technologies = self._extract_recommended_technologies(
            domain, business_model, technical_patterns
        )

        # Identify common challenges
        common_challenges = self._identify_common_challenges(domain, technical_patterns)

        # Extract official documentation links
        official_docs_links = self._extract_official_docs_links(
            domain, technical_patterns
        )

        # Calculate research quality score
        quality_score = self._calculate_research_quality_score(
            domain_overview, technical_patterns, best_practices, official_docs_links
        )

        context = ResearchContext(
            domain_overview=domain_overview,
            technical_patterns=technical_patterns,
            best_practices=best_practices,
            common_challenges=common_challenges,
            recommended_technologies=recommended_technologies,
            validation_approaches=validation_approaches,
            official_documentation_links=official_docs_links,
            competitor_analysis=competitor_analysis,
            research_timestamp=datetime.utcnow(),
            research_quality_score=quality_score,
        )

        # Cache the result
        self._research_cache[cache_key] = (context, datetime.utcnow())

        return context

    async def _research_domain_overview(self, domain: str, description: str) -> str:
        """Research domain overview with focus on official documentation."""
        if not self.web_search_client:
            return self._get_fallback_domain_overview(domain)

        # Prioritize official documentation in search queries
        official_queries = [
            f"{domain} architecture patterns site:docs.python.org OR site:flask.palletsprojects.com",
            f"{domain} best practices official documentation",
            f"{domain} development guide official docs",
        ]

        try:
            overview_parts = []
            for query in official_queries:
                results = await self._web_search_with_official_priority(
                    query, max_results=3
                )
                for result in results[:2]:  # Take top 2 from each query
                    if result.is_official_docs:
                        overview_parts.append(f"From {result.domain}: {result.snippet}")

            if overview_parts:
                return " ".join(overview_parts)
            else:
                return self._get_fallback_domain_overview(domain)

        except Exception as e:
            logger.error(f"Error researching domain overview: {e}")
            return self._get_fallback_domain_overview(domain)

    async def _research_technical_patterns(
        self, domain: str, business_model: str
    ) -> List[str]:
        """Research technical patterns with official documentation preference."""
        if not self.web_search_client:
            return self._get_fallback_technical_patterns(domain)

        patterns = []
        domain_queries = self.domain_query_templates.get(domain, [])

        try:
            for query in domain_queries[:3]:  # Limit to 3 queries to avoid API limits
                results = await self._web_search_with_official_priority(
                    query, max_results=5
                )

                # Extract patterns from official documentation first
                for result in results:
                    if result.is_official_docs:
                        pattern = self._extract_pattern_from_snippet(result.snippet)
                        if pattern:
                            patterns.append(f"{pattern} (from {result.domain})")

                # If no official patterns found, use other sources
                if not patterns:
                    for result in results:
                        pattern = self._extract_pattern_from_snippet(result.snippet)
                        if pattern:
                            patterns.append(pattern)
                            break

            return (
                patterns[:5]
                if patterns
                else self._get_fallback_technical_patterns(domain)
            )

        except Exception as e:
            logger.error(f"Error researching technical patterns: {e}")
            return self._get_fallback_technical_patterns(domain)

    async def _research_best_practices(self, domain: str) -> List[str]:
        """Research best practices from official sources."""
        if not self.web_search_client:
            return self._get_fallback_best_practices(domain)

        # Focus on official documentation for best practices
        official_practice_queries = [
            f"{domain} security best practices site:docs.aws.amazon.com OR site:cloud.google.com",
            f"{domain} performance optimization official documentation",
            f"{domain} testing patterns official guide",
        ]

        practices = []

        try:
            for query in official_practice_queries:
                results = await self._web_search_with_official_priority(
                    query, max_results=3
                )

                for result in results:
                    if result.is_official_docs:
                        practice = self._extract_best_practice_from_snippet(
                            result.snippet
                        )
                        if practice:
                            practices.append(f"{practice} (Official: {result.domain})")

            return (
                practices[:5]
                if practices
                else self._get_fallback_best_practices(domain)
            )

        except Exception as e:
            logger.error(f"Error researching best practices: {e}")
            return self._get_fallback_best_practices(domain)

    async def _research_validation_approaches(self, domain: str) -> List[str]:
        """Research validation approaches from official documentation."""
        if not self.web_search_client:
            return self._get_fallback_validation_approaches(domain)

        validation_queries = [
            f"{domain} testing validation official documentation",
            f"{domain} quality assurance patterns site:docs.python.org",
            f"{domain} monitoring logging best practices official",
        ]

        approaches = []

        try:
            for query in validation_queries:
                results = await self._web_search_with_official_priority(
                    query, max_results=3
                )

                for result in results:
                    if result.is_official_docs:
                        approach = self._extract_validation_approach_from_snippet(
                            result.snippet
                        )
                        if approach:
                            approaches.append(f"{approach} (from {result.domain})")

            return (
                approaches[:3]
                if approaches
                else self._get_fallback_validation_approaches(domain)
            )

        except Exception as e:
            logger.error(f"Error researching validation approaches: {e}")
            return self._get_fallback_validation_approaches(domain)

    async def _research_competitors(self, domain: str, description: str) -> List[str]:
        """Research competitors and similar solutions."""
        if not self.web_search_client:
            return self._get_fallback_competitors(domain)

        # Extract key terms from description for competitor research
        key_terms = self._extract_key_terms_from_description(description)
        competitor_queries = [
            f"{domain} {key_terms} competitors alternatives",
            f"successful {domain} companies similar to {key_terms}",
            f"{domain} market leaders {key_terms}",
        ]

        competitors = []

        try:
            for query in competitor_queries[:2]:  # Limit competitor research
                results = await self._web_search_with_official_priority(
                    query, max_results=3
                )

                for result in results:
                    competitor_info = self._extract_competitor_info_from_snippet(
                        result.snippet
                    )
                    if competitor_info:
                        competitors.append(competitor_info)

            return (
                competitors[:5]
                if competitors
                else self._get_fallback_competitors(domain)
            )

        except Exception as e:
            logger.error(f"Error researching competitors: {e}")
            return self._get_fallback_competitors(domain)

    async def _web_search_with_official_priority(
        self, query: str, max_results: int = 10
    ) -> List[SearchResult]:
        """Perform web search with prioritization of official documentation sources."""
        if not self.web_search_client:
            return []

        try:
            # This would integrate with actual web search API (Google, Bing, etc.)
            # For now, return mock results that demonstrate the prioritization
            mock_results = [
                SearchResult(
                    title=f"Official Documentation - {query[:30]}...",
                    url=f"https://docs.python.org/guide/{query.replace(' ', '-')}",
                    snippet=f"Official documentation for {query}. Best practices and patterns...",
                    domain="docs.python.org",
                    relevance_score=9.5,
                    is_official_docs=True,
                    content_type="documentation",
                ),
                SearchResult(
                    title=f"Stack Overflow - {query[:30]}...",
                    url="https://stackoverflow.com/questions/123456",
                    snippet=f"Community discussion about {query}...",
                    domain="stackoverflow.com",
                    relevance_score=8.0,
                    is_official_docs=False,
                    content_type="community",
                ),
            ]

            # Sort results with official docs prioritized
            return self._prioritize_documentation_sources(mock_results)

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    def _prioritize_documentation_sources(
        self, search_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Sort search results with official documentation sources prioritized.

        CONSTRAINT: Prefer official vendor documentation sources.
        Priority order: Official docs > GitHub official repos > Stack Overflow > Blog posts
        """

        def get_priority_score(result: SearchResult) -> tuple:
            # Check if domain is in official docs list
            is_official = result.domain in self.official_docs_domains

            # Assign priority categories
            if is_official and result.content_type == "documentation":
                priority_category = 0  # Highest priority
            elif result.domain == "github.com" and "official" in result.title.lower():
                priority_category = 1  # Official GitHub repos
            elif result.domain == "stackoverflow.com":
                priority_category = 2  # Community Q&A
            else:
                priority_category = 3  # Other sources

            # Return tuple for sorting: (priority_category, -relevance_score)
            # Lower priority_category = higher priority
            # Higher relevance_score = higher priority (hence negative)
            return (priority_category, -result.relevance_score)

        # Sort by priority, then by relevance score
        sorted_results = sorted(search_results, key=get_priority_score)

        # Mark official docs
        for result in sorted_results:
            result.is_official_docs = result.domain in self.official_docs_domains

        return sorted_results

    def _extract_pattern_from_snippet(self, snippet: str) -> Optional[str]:
        """Extract technical pattern from search snippet."""
        # Simple pattern extraction - could be enhanced with NLP
        pattern_keywords = ["pattern", "architecture", "design", "approach", "method"]

        for keyword in pattern_keywords:
            if keyword in snippet.lower():
                # Extract sentence containing the pattern keyword
                sentences = snippet.split(". ")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()

        return None

    def _extract_best_practice_from_snippet(self, snippet: str) -> Optional[str]:
        """Extract best practice from search snippet."""
        practice_keywords = [
            "best practice",
            "recommendation",
            "should",
            "avoid",
            "ensure",
        ]

        for keyword in practice_keywords:
            if keyword in snippet.lower():
                sentences = snippet.split(". ")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()

        return None

    def _extract_validation_approach_from_snippet(self, snippet: str) -> Optional[str]:
        """Extract validation approach from snippet."""
        validation_keywords = ["test", "validate", "verify", "check", "monitor"]

        for keyword in validation_keywords:
            if keyword in snippet.lower():
                sentences = snippet.split(". ")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()

        return None

    def _extract_competitor_info_from_snippet(self, snippet: str) -> Optional[str]:
        """Extract competitor information from snippet."""
        # Look for company names and product descriptions
        if any(
            word in snippet.lower()
            for word in ["company", "platform", "service", "solution"]
        ):
            return snippet[:100] + "..." if len(snippet) > 100 else snippet

        return None

    def _extract_key_terms_from_description(self, description: str) -> str:
        """Extract key terms from business description."""
        # Simple keyword extraction - could use NLP for better results
        common_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "a",
            "an",
        }
        words = re.findall(r"\b\w+\b", description.lower())
        key_words = [w for w in words if len(w) > 3 and w not in common_words]
        return " ".join(key_words[:3])  # Top 3 key terms

    def _extract_recommended_technologies(
        self, domain: str, business_model: str, patterns: List[str]
    ) -> List[str]:
        """Extract recommended technologies based on research."""
        tech_recommendations = []

        # Domain-specific technology recommendations
        if domain == "saas":
            tech_recommendations.extend(
                [
                    "Flask/FastAPI for Python backend",
                    "PostgreSQL for multi-tenant data",
                    "Redis for session management",
                    "Stripe for subscription billing",
                ]
            )
        elif domain == "e_commerce":
            tech_recommendations.extend(
                [
                    "Django for e-commerce features",
                    "Celery for order processing",
                    "Elasticsearch for product search",
                    "Payment gateway integration (Stripe, PayPal)",
                ]
            )
        elif domain == "mobile_app":
            tech_recommendations.extend(
                [
                    "RESTful API backend",
                    "JWT for mobile authentication",
                    "Push notification service",
                    "Cloud file storage (AWS S3)",
                ]
            )

        return tech_recommendations[:4]

    def _identify_common_challenges(
        self, domain: str, patterns: List[str]
    ) -> List[str]:
        """Identify common challenges based on domain and patterns."""
        # Domain-specific challenges
        domain_challenges = {
            "saas": [
                "Multi-tenancy data isolation",
                "Subscription billing management",
                "User onboarding and retention",
                "API rate limiting and quotas",
            ],
            "e_commerce": [
                "Payment security and PCI compliance",
                "Inventory management complexity",
                "Cart abandonment optimization",
                "Order fulfillment automation",
            ],
            "mobile_app": [
                "Cross-platform compatibility",
                "Offline data synchronization",
                "App store approval process",
                "Battery and performance optimization",
            ],
            "fintech": [
                "Financial regulatory compliance",
                "Transaction security and fraud detection",
                "Real-time payment processing",
                "Data privacy and encryption",
            ],
        }

        return domain_challenges.get(
            domain, ["Technical scalability", "User experience optimization"]
        )[:4]

    def _extract_official_docs_links(
        self, domain: str, patterns: List[str]
    ) -> List[str]:
        """Extract official documentation links relevant to the domain."""
        # This would normally extract actual links from search results
        domain_docs = {
            "saas": [
                "https://flask.palletsprojects.com/patterns/",
                "https://docs.python.org/3/library/",
                "https://docs.aws.amazon.com/architecture-center/",
            ],
            "e_commerce": [
                "https://docs.djangoproject.com/en/stable/",
                "https://stripe.com/docs/api",
                "https://docs.aws.amazon.com/s3/",
            ],
            "mobile_app": [
                "https://flask-restx.readthedocs.io/",
                "https://pyjwt.readthedocs.io/",
                "https://docs.aws.amazon.com/sns/",
            ],
        }

        return domain_docs.get(domain, ["https://docs.python.org/"])[:3]

    def _calculate_research_quality_score(
        self,
        overview: str,
        patterns: List[str],
        practices: List[str],
        official_links: List[str],
    ) -> float:
        """Calculate research quality score based on content and sources."""
        score = 0.0

        # Overview quality
        if len(overview) > 100:
            score += 2.5

        # Pattern quantity and quality
        official_patterns = len(
            [p for p in patterns if "Official:" in p or "from docs." in p]
        )
        score += min(official_patterns * 1.5, 3.0)  # Max 3 points for official patterns

        # Best practices quality
        official_practices = len([p for p in practices if "Official:" in p])
        score += min(
            official_practices * 1.0, 2.0
        )  # Max 2 points for official practices

        # Official documentation links
        score += min(
            len(official_links) * 0.5, 2.5
        )  # Max 2.5 points for official links

        return min(score, 10.0)  # Cap at 10.0

    # Fallback methods for when web search is not available
    def _get_fallback_domain_overview(self, domain: str) -> str:
        overviews = {
            "saas": "SaaS applications require multi-tenant architecture, subscription management, and scalable user authentication systems.",
            "e_commerce": "E-commerce platforms need secure payment processing, inventory management, and order fulfillment workflows.",
            "mobile_app": "Mobile applications require responsive APIs, offline capability, and push notification systems.",
        }
        return overviews.get(
            domain, f"Domain overview for {domain} applications and best practices."
        )

    def _get_fallback_technical_patterns(self, domain: str) -> List[str]:
        patterns = {
            "saas": [
                "Multi-tenant database schema with tenant isolation",
                "JWT-based authentication with role-based access control",
                "Subscription billing with webhook handling",
                "API rate limiting per tenant",
            ],
            "e_commerce": [
                "Shopping cart session management",
                "Order state machine for order processing",
                "Inventory reservation and release patterns",
                "Payment processing with idempotency",
            ],
        }
        return patterns.get(
            domain, ["RESTful API design", "Database modeling patterns"]
        )

    def _get_fallback_best_practices(self, domain: str) -> List[str]:
        practices = {
            "saas": [
                "Implement proper data isolation between tenants",
                "Use environment-based configuration management",
                "Implement comprehensive API logging and monitoring",
            ],
            "e_commerce": [
                "Secure payment data with PCI compliance",
                "Implement inventory locking for concurrent orders",
                "Use database transactions for order processing",
            ],
        }
        return practices.get(
            domain,
            ["Follow security best practices", "Implement proper error handling"],
        )

    def _get_fallback_validation_approaches(self, domain: str) -> List[str]:
        return [
            "Unit testing with pytest framework",
            "Integration testing for API endpoints",
            "Load testing for performance validation",
        ]

    def _get_fallback_competitors(self, domain: str) -> List[str]:
        competitors = {
            "saas": ["Salesforce", "HubSpot", "Slack", "Zoom"],
            "e_commerce": ["Shopify", "WooCommerce", "Magento", "BigCommerce"],
            "mobile_app": [
                "Native mobile apps",
                "Progressive Web Apps",
                "React Native solutions",
            ],
        }
        return competitors.get(domain, ["Market leaders in the domain"])[:3]

    async def conduct_gap_targeted_research(
        self,
        gaps: List[KnowledgeGap],
        domain: str,
        business_model: str,
        concept_description: str,
        max_gaps_to_research: int = 5,
    ) -> ResearchContext:
        """Conduct research specifically targeting identified knowledge gaps.

        Args:
            gaps: List of knowledge gaps to target
            domain: Business domain
            business_model: Business model
            concept_description: Description of the concept
            max_gaps_to_research: Maximum number of gaps to research

        Returns:
            Research context focused on addressing the gaps
        """
        logger.info(f"Conducting gap-targeted research for {len(gaps)} gaps in {domain}")

        # Prioritize gaps by priority and confidence score
        prioritized_gaps = sorted(
            gaps,
            key=lambda g: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[g.priority],
                g.confidence_score,
            ),
            reverse=True,
        )[:max_gaps_to_research]

        # Generate targeted research queries for each gap
        gap_specific_contexts = []

        for gap in prioritized_gaps:
            try:
                gap_context = await self._research_specific_gap(
                    gap, domain, business_model, concept_description
                )
                if gap_context:
                    gap_specific_contexts.append(gap_context)
                    logger.debug(f"Completed research for gap: {gap.id}")
            except Exception as e:
                logger.warning(f"Failed to research gap {gap.id}: {e}")

        # Merge all gap-specific contexts into comprehensive result
        if gap_specific_contexts:
            merged_context = await self._merge_gap_research_contexts(
                gap_specific_contexts, domain, concept_description
            )
            logger.info(
                f"Gap-targeted research completed: {len(gap_specific_contexts)} gaps researched"
            )
            return merged_context
        else:
            # Fallback to general research if gap-specific research fails
            logger.warning("Gap-targeted research failed, falling back to general research")
            return await self.gather_business_domain_context(
                domain, business_model, concept_description
            )

    async def _research_specific_gap(
        self,
        gap: KnowledgeGap,
        domain: str,
        business_model: str,
        concept_description: str,
    ) -> Optional[ResearchContext]:
        """Research a specific knowledge gap."""
        # Generate gap-specific queries
        gap_queries = self._generate_gap_specific_queries(gap, domain, business_model)

        # Conduct research for each query
        research_results = []
        for query in gap_queries[:3]:  # Limit queries per gap
            try:
                results = await self._web_search_with_official_priority(query, max_results=5)
                research_results.extend(results)
            except Exception as e:
                logger.warning(f"Query '{query}' failed: {e}")

        if not research_results:
            return None

        # Convert results to research context
        return await self._convert_results_to_context(
            research_results, gap, domain, concept_description
        )

    def _generate_gap_specific_queries(
        self, gap: KnowledgeGap, domain: str, business_model: str
    ) -> List[str]:
        """Generate specific research queries for a knowledge gap."""
        queries = []

        # Base query combining gap category and domain
        base_query = f"{gap.category.replace('_', ' ')} {domain} official documentation"
        queries.append(base_query)

        # Extract key terms from gap description
        gap_terms = self._extract_gap_terms(gap.description)
        if gap_terms:
            gap_query = f"{domain} {gap_terms} best practices site:docs.python.org OR site:flask.palletsprojects.com"
            queries.append(gap_query)

        # Category-specific queries with official docs preference
        category_queries = self._get_category_specific_queries(gap.category, domain)
        queries.extend(category_queries[:2])

        # Business model specific queries
        if business_model and business_model != "general":
            model_query = f"{business_model} {gap.category.replace('_', ' ')} patterns {domain}"
            queries.append(model_query)

        return queries

    def _extract_gap_terms(self, gap_description: str) -> str:
        """Extract key terms from gap description for targeted queries."""
        # Remove common prefix
        clean_desc = gap_description.replace("Missing or insufficient information about:", "").strip()
        
        # Extract meaningful terms
        meaningful_words = []
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        
        words = re.findall(r'\b\w+\b', clean_desc.lower())
        for word in words:
            if len(word) > 3 and word not in stop_words:
                meaningful_words.append(word)
        
        return ' '.join(meaningful_words[:3])  # Top 3 meaningful terms

    def _get_category_specific_queries(self, category: str, domain: str) -> List[str]:
        """Get category-specific research queries."""
        category_query_map = {
            "business_model": [
                f"{domain} monetization strategies official guide",
                f"{domain} pricing models best practices",
                f"{domain} revenue streams documentation",
            ],
            "technical_requirements": [
                f"{domain} architecture patterns official documentation",
                f"{domain} technical specifications site:docs.python.org",
                f"{domain} system requirements best practices",
            ],
            "user_experience": [
                f"{domain} user interface design guidelines",
                f"{domain} user experience best practices",
                f"{domain} accessibility requirements documentation",
            ],
            "integration": [
                f"{domain} API integration patterns official docs",
                f"{domain} third-party integrations best practices",
                f"{domain} webhook patterns documentation",
            ],
            "validation": [
                f"{domain} testing strategies official documentation",
                f"{domain} quality assurance best practices",
                f"{domain} monitoring patterns site:docs.python.org",
            ],
            "deployment": [
                f"{domain} deployment strategies documentation",
                f"{domain} infrastructure patterns official guide",
                f"{domain} scaling best practices",
            ],
        }
        
        return category_query_map.get(category, [])

    async def _convert_results_to_context(
        self,
        search_results: List[SearchResult],
        gap: KnowledgeGap,
        domain: str,
        concept_description: str,
    ) -> ResearchContext:
        """Convert search results to research context focused on the gap."""
        # Analyze results and extract information relevant to the gap
        technical_patterns = []
        best_practices = []
        official_docs = []
        
        for result in search_results:
            if result.is_official_docs:
                official_docs.append(result.url)
                
            # Extract patterns and practices from snippets
            if gap.category in ["technical_requirements", "deployment"]:
                pattern = self._extract_pattern_from_snippet(result.snippet)
                if pattern:
                    technical_patterns.append(f"{pattern} (from {result.domain})")
            
            if any(word in result.snippet.lower() for word in ["best practice", "recommend", "should"]):
                practice = self._extract_best_practice_from_snippet(result.snippet)
                if practice:
                    best_practices.append(f"{practice} (from {result.domain})")

        # Generate domain overview focused on the gap
        gap_focused_overview = f"Research focused on {gap.category.replace('_', ' ')} for {domain} applications, addressing: {gap.description}"

        # Generate recommendations based on gap category
        recommendations = self._generate_gap_specific_recommendations(gap, domain)
        
        # Calculate quality score based on official sources
        official_source_count = len(official_docs)
        quality_score = min(10.0, official_source_count * 2.0 + len(technical_patterns) * 0.5)

        return ResearchContext(
            domain_overview=gap_focused_overview,
            technical_patterns=technical_patterns[:5],
            best_practices=best_practices[:5],
            common_challenges=self._identify_gap_specific_challenges(gap, domain),
            recommended_technologies=recommendations,
            validation_approaches=self._generate_gap_validation_approaches(gap),
            official_documentation_links=official_docs[:5],
            competitor_analysis=[],  # Not gap-specific
            research_timestamp=datetime.utcnow(),
            research_quality_score=quality_score,
        )

    def _generate_gap_specific_recommendations(self, gap: KnowledgeGap, domain: str) -> List[str]:
        """Generate technology recommendations specific to a knowledge gap."""
        recommendations = []
        
        if gap.category == "business_model":
            recommendations.extend([
                "Stripe for payment processing",
                "Chargebee for subscription management",
                "Analytics platform (Google Analytics, Mixpanel)",
            ])
        elif gap.category == "technical_requirements":
            recommendations.extend([
                "Flask/FastAPI for backend development",
                "PostgreSQL for data persistence",
                "Redis for caching and sessions",
                "Docker for containerization",
            ])
        elif gap.category == "integration":
            recommendations.extend([
                "REST API design patterns",
                "Webhook implementation for real-time updates",
                "OAuth 2.0 for third-party authentication",
            ])
        elif gap.category == "validation":
            recommendations.extend([
                "pytest for unit testing",
                "pytest-asyncio for async testing",
                "Sentry for error monitoring",
                "Prometheus for metrics",
            ])
        elif gap.category == "deployment":
            recommendations.extend([
                "Docker containerization",
                "GitHub Actions for CI/CD",
                "AWS/GCP for cloud hosting",
                "Kubernetes for orchestration",
            ])
        
        return recommendations[:4]

    def _identify_gap_specific_challenges(self, gap: KnowledgeGap, domain: str) -> List[str]:
        """Identify challenges specific to a knowledge gap."""
        challenges = []
        
        if gap.category == "business_model":
            challenges.extend([
                "Pricing optimization and market acceptance",
                "Customer acquisition cost management",
                "Revenue stream diversification",
            ])
        elif gap.category == "technical_requirements":
            challenges.extend([
                "System scalability and performance",
                "Security and data protection",
                "Integration complexity management",
            ])
        elif gap.category == "user_experience":
            challenges.extend([
                "Cross-platform consistency",
                "Accessibility compliance",
                "User adoption and retention",
            ])
        elif gap.category == "integration":
            challenges.extend([
                "API version management",
                "Third-party service reliability",
                "Data synchronization consistency",
            ])
        
        return challenges[:3]

    def _generate_gap_validation_approaches(self, gap: KnowledgeGap) -> List[str]:
        """Generate validation approaches specific to a gap category."""
        approaches = []
        
        if gap.category == "business_model":
            approaches.extend([
                "A/B testing for pricing strategies",
                "Customer feedback and survey analysis",
                "Revenue and conversion tracking",
            ])
        elif gap.category == "technical_requirements":
            approaches.extend([
                "Performance benchmarking and load testing",
                "Security auditing and penetration testing",
                "Integration testing with external services",
            ])
        elif gap.category == "user_experience":
            approaches.extend([
                "User acceptance testing (UAT)",
                "Usability testing and user interviews",
                "Accessibility compliance testing",
            ])
        
        return approaches[:3]

    async def _merge_gap_research_contexts(
        self, contexts: List[ResearchContext], domain: str, concept_description: str
    ) -> ResearchContext:
        """Merge multiple gap-specific research contexts into a comprehensive result."""
        if not contexts:
            return None
        
        if len(contexts) == 1:
            return contexts[0]

        # Merge all fields, removing duplicates
        all_patterns = []
        all_practices = []
        all_challenges = []
        all_technologies = []
        all_validation = []
        all_docs = []
        
        for context in contexts:
            all_patterns.extend(context.technical_patterns)
            all_practices.extend(context.best_practices)
            all_challenges.extend(context.common_challenges)
            all_technologies.extend(context.recommended_technologies)
            all_validation.extend(context.validation_approaches)
            all_docs.extend(context.official_documentation_links)

        # Remove duplicates while preserving order
        def dedupe_list(items: List[str]) -> List[str]:
            seen = set()
            result = []
            for item in items:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result

        merged_patterns = dedupe_list(all_patterns)
        merged_practices = dedupe_list(all_practices)
        merged_challenges = dedupe_list(all_challenges)
        merged_technologies = dedupe_list(all_technologies)
        merged_validation = dedupe_list(all_validation)
        merged_docs = dedupe_list(all_docs)

        # Generate comprehensive overview
        overview = f"Comprehensive research for {domain} covering multiple knowledge gaps: {concept_description[:100]}..."

        # Calculate merged quality score
        avg_quality = sum(c.research_quality_score for c in contexts) / len(contexts)

        return ResearchContext(
            domain_overview=overview,
            technical_patterns=merged_patterns[:8],  # More patterns from merged research
            best_practices=merged_practices[:6],
            common_challenges=merged_challenges[:5],
            recommended_technologies=merged_technologies[:6],
            validation_approaches=merged_validation[:4],
            official_documentation_links=merged_docs[:8],
            competitor_analysis=[],  # Keep empty for gap-focused research
            research_timestamp=datetime.utcnow(),
            research_quality_score=min(10.0, avg_quality + 1.0),  # Boost for comprehensive research
        )

    async def enhance_research_with_gaps(
        self,
        base_research: ResearchContext,
        gaps: List[KnowledgeGap],
        domain: str,
        business_model: str,
        concept_description: str,
    ) -> ResearchContext:
        """Enhance existing research context by addressing remaining knowledge gaps.

        Args:
            base_research: Existing research context
            gaps: Knowledge gaps to address
            domain: Business domain
            business_model: Business model
            concept_description: Concept description

        Returns:
            Enhanced research context
        """
        if not gaps:
            return base_research

        logger.info(f"Enhancing existing research with {len(gaps)} additional gaps")

        # Conduct gap-specific research
        gap_research = await self.conduct_gap_targeted_research(
            gaps, domain, business_model, concept_description
        )

        # Merge with base research
        enhanced_research = await self._merge_research_contexts(base_research, gap_research)
        
        logger.info("Research enhancement completed")
        return enhanced_research

    async def _merge_research_contexts(
        self, context1: ResearchContext, context2: ResearchContext
    ) -> ResearchContext:
        """Merge two research contexts intelligently."""
        # Combine and deduplicate lists
        merged_patterns = list(set(context1.technical_patterns + context2.technical_patterns))[:8]
        merged_practices = list(set(context1.best_practices + context2.best_practices))[:6]
        merged_challenges = list(set(context1.common_challenges + context2.common_challenges))[:5]
        merged_technologies = list(set(context1.recommended_technologies + context2.recommended_technologies))[:6]
        merged_validation = list(set(context1.validation_approaches + context2.validation_approaches))[:4]
        merged_docs = list(set(context1.official_documentation_links + context2.official_documentation_links))[:8]
        merged_competitors = list(set(context1.competitor_analysis + context2.competitor_analysis))[:4]

        # Use the overview from the higher quality research, or combine if similar quality
        quality_diff = abs(context1.research_quality_score - context2.research_quality_score)
        if quality_diff < 1.0:  # Similar quality, combine overviews
            merged_overview = f"{context1.domain_overview} Enhanced with additional gap analysis: {context2.domain_overview}"[:500]
        else:
            # Use the higher quality overview
            base_context = context1 if context1.research_quality_score > context2.research_quality_score else context2
            merged_overview = base_context.domain_overview

        return ResearchContext(
            domain_overview=merged_overview,
            technical_patterns=merged_patterns,
            best_practices=merged_practices,
            common_challenges=merged_challenges,
            recommended_technologies=merged_technologies,
            validation_approaches=merged_validation,
            official_documentation_links=merged_docs,
            competitor_analysis=merged_competitors,
            research_timestamp=datetime.utcnow(),
            research_quality_score=max(context1.research_quality_score, context2.research_quality_score) + 0.5,  # Small boost for merged research
        )
