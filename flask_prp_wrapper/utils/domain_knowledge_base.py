"""Domain-specific knowledge base for gap analysis and coverage validation."""

import logging
from typing import Dict, List

from ..models.coverage_metrics import DomainCoverageRequirement

logger = logging.getLogger(__name__)


class DomainKnowledgeBase:
    """Central repository for domain-specific knowledge and requirements."""

    def __init__(self):
        """Initialize the domain knowledge base."""
        self._domain_requirements = self._load_domain_requirements()
        self._prp_template_requirements = self._load_prp_template_requirements()

    def _load_domain_requirements(self) -> Dict[str, List[DomainCoverageRequirement]]:
        """Load domain-specific coverage requirements."""
        return {
            "saas": [
                DomainCoverageRequirement(
                    domain="saas",
                    category="business_model",
                    requirement="Subscription tier structure and pricing model",
                    priority="critical",
                    coverage_weight=0.2,
                    validation_criteria=[
                        "Subscription tiers defined",
                        "Pricing model specified",
                        "Billing cycle determined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="saas",
                    category="technical_requirements",
                    requirement="Multi-tenant architecture and data isolation",
                    priority="critical",
                    coverage_weight=0.25,
                    validation_criteria=[
                        "Tenant isolation strategy defined",
                        "Database schema approach specified",
                        "Security boundaries established",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="saas",
                    category="user_management",
                    requirement="User authentication and authorization system",
                    priority="high",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Authentication method chosen",
                        "Role-based access control defined",
                        "User registration flow specified",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="saas",
                    category="integration",
                    requirement="Third-party service integrations",
                    priority="high",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Payment gateway integration",
                        "Email service integration",
                        "Analytics integration",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="saas",
                    category="validation",
                    requirement="Performance monitoring and testing strategy",
                    priority="medium",
                    coverage_weight=0.1,
                    validation_criteria=[
                        "Monitoring solution specified",
                        "Testing approach defined",
                        "Performance metrics identified",
                    ],
                ),
            ],
            "e_commerce": [
                DomainCoverageRequirement(
                    domain="e_commerce",
                    category="business_model",
                    requirement="Product catalog and inventory management",
                    priority="critical",
                    coverage_weight=0.2,
                    validation_criteria=[
                        "Product categorization defined",
                        "Inventory tracking specified",
                        "Stock management rules established",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="e_commerce",
                    category="technical_requirements",
                    requirement="Order processing and payment system",
                    priority="critical",
                    coverage_weight=0.25,
                    validation_criteria=[
                        "Order workflow defined",
                        "Payment processing specified",
                        "Security compliance addressed",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="e_commerce",
                    category="user_experience",
                    requirement="Shopping cart and checkout experience",
                    priority="high",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Cart functionality specified",
                        "Checkout flow defined",
                        "Guest checkout option addressed",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="e_commerce",
                    category="integration",
                    requirement="Shipping and fulfillment integrations",
                    priority="high",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Shipping carrier integration",
                        "Fulfillment process defined",
                        "Tracking system specified",
                    ],
                ),
            ],
            "mobile_app": [
                DomainCoverageRequirement(
                    domain="mobile_app",
                    category="technical_requirements",
                    requirement="Mobile platform and development approach",
                    priority="critical",
                    coverage_weight=0.25,
                    validation_criteria=[
                        "Target platforms specified (iOS/Android)",
                        "Development approach chosen (native/cross-platform)",
                        "Device compatibility requirements defined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="mobile_app",
                    category="user_experience",
                    requirement="Mobile-first UI/UX design patterns",
                    priority="high",
                    coverage_weight=0.2,
                    validation_criteria=[
                        "Navigation patterns defined",
                        "Touch interaction patterns specified",
                        "Responsive design approach outlined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="mobile_app",
                    category="technical_requirements",
                    requirement="Offline functionality and data synchronization",
                    priority="high",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Offline capabilities defined",
                        "Data sync strategy specified",
                        "Conflict resolution approach outlined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="mobile_app",
                    category="integration",
                    requirement="Push notifications and backend integration",
                    priority="medium",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Push notification strategy defined",
                        "Backend API integration specified",
                        "Real-time features outlined",
                    ],
                ),
            ],
            "marketplace": [
                DomainCoverageRequirement(
                    domain="marketplace",
                    category="business_model",
                    requirement="Multi-sided market structure and monetization",
                    priority="critical",
                    coverage_weight=0.25,
                    validation_criteria=[
                        "Marketplace participants defined",
                        "Revenue model specified",
                        "Commission structure outlined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="marketplace",
                    category="user_management",
                    requirement="Multi-role user management system",
                    priority="critical",
                    coverage_weight=0.2,
                    validation_criteria=[
                        "User roles defined (buyers, sellers, admins)",
                        "Registration flows specified",
                        "Verification processes outlined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="marketplace",
                    category="technical_requirements",
                    requirement="Transaction processing and escrow system",
                    priority="high",
                    coverage_weight=0.15,
                    validation_criteria=[
                        "Payment flow between parties defined",
                        "Dispute resolution process specified",
                        "Escrow mechanism outlined",
                    ],
                ),
            ],
            "fintech": [
                DomainCoverageRequirement(
                    domain="fintech",
                    category="technical_requirements",
                    requirement="Financial regulatory compliance",
                    priority="critical",
                    coverage_weight=0.3,
                    validation_criteria=[
                        "Regulatory requirements identified",
                        "Compliance framework specified",
                        "Audit trail requirements defined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="fintech",
                    category="technical_requirements",
                    requirement="Data security and encryption standards",
                    priority="critical",
                    coverage_weight=0.25,
                    validation_criteria=[
                        "Encryption standards specified",
                        "Data protection measures defined",
                        "Security audit requirements outlined",
                    ],
                ),
                DomainCoverageRequirement(
                    domain="fintech",
                    category="integration",
                    requirement="Financial institution and payment processor integration",
                    priority="high",
                    coverage_weight=0.2,
                    validation_criteria=[
                        "Banking integration approach defined",
                        "Payment processor selection specified",
                        "API security requirements outlined",
                    ],
                ),
            ],
        }

    def _load_prp_template_requirements(self) -> List[DomainCoverageRequirement]:
        """Load requirements based on PRP template structure."""
        return [
            DomainCoverageRequirement(
                domain="general",
                category="goal_definition",
                requirement="Clear feature goal and deliverable specification",
                priority="critical",
                coverage_weight=0.15,
                validation_criteria=[
                    "Feature goal clearly defined",
                    "Deliverable specified",
                    "Success definition provided",
                ],
            ),
            DomainCoverageRequirement(
                domain="general",
                category="user_persona",
                requirement="Target user and use case identification",
                priority="high",
                coverage_weight=0.1,
                validation_criteria=[
                    "Target user defined",
                    "Use case specified",
                    "User journey outlined",
                ],
            ),
            DomainCoverageRequirement(
                domain="general",
                category="technical_implementation",
                requirement="Implementation blueprint with task breakdown",
                priority="critical",
                coverage_weight=0.25,
                validation_criteria=[
                    "Data models defined",
                    "Implementation tasks specified",
                    "Integration points identified",
                ],
            ),
            DomainCoverageRequirement(
                domain="general",
                category="validation",
                requirement="Comprehensive validation loop specification",
                priority="high",
                coverage_weight=0.15,
                validation_criteria=[
                    "Syntax validation commands provided",
                    "Unit testing approach specified",
                    "Integration testing defined",
                ],
            ),
            DomainCoverageRequirement(
                domain="general",
                category="context",
                requirement="Complete context and reference documentation",
                priority="high",
                coverage_weight=0.2,
                validation_criteria=[
                    "Documentation references provided",
                    "Codebase patterns identified",
                    "Known gotchas documented",
                ],
            ),
        ]

    def get_domain_requirements(self, domain: str) -> List[DomainCoverageRequirement]:
        """Get coverage requirements for a specific domain.

        Args:
            domain: Business domain name

        Returns:
            List of coverage requirements for the domain
        """
        domain_reqs = self._domain_requirements.get(domain, [])
        general_reqs = self._prp_template_requirements

        return domain_reqs + general_reqs

    def get_all_domains(self) -> List[str]:
        """Get list of all supported domains.

        Returns:
            List of domain names
        """
        return list(self._domain_requirements.keys())

    def get_requirement_by_category(
        self, domain: str, category: str
    ) -> List[DomainCoverageRequirement]:
        """Get requirements for a specific domain and category.

        Args:
            domain: Business domain name
            category: Requirement category

        Returns:
            List of matching requirements
        """
        domain_reqs = self.get_domain_requirements(domain)
        return [req for req in domain_reqs if req.category == category]

    def get_critical_requirements(self, domain: str) -> List[DomainCoverageRequirement]:
        """Get critical priority requirements for a domain.

        Args:
            domain: Business domain name

        Returns:
            List of critical requirements
        """
        domain_reqs = self.get_domain_requirements(domain)
        return [req for req in domain_reqs if req.priority == "critical"]

    def calculate_domain_coverage_weight(self, domain: str) -> float:
        """Calculate total coverage weight for a domain.

        Args:
            domain: Business domain name

        Returns:
            Total coverage weight (should sum to 1.0)
        """
        domain_reqs = self.get_domain_requirements(domain)
        return sum(req.coverage_weight for req in domain_reqs)

    def get_coverage_template(self, domain: str) -> Dict[str, List[str]]:
        """Get a coverage template showing all areas that need coverage.

        Args:
            domain: Business domain name

        Returns:
            Dictionary mapping categories to requirement descriptions
        """
        domain_reqs = self.get_domain_requirements(domain)
        template: Dict[str, List[str]] = {}

        for req in domain_reqs:
            if req.category not in template:
                template[req.category] = []
            template[req.category].append(req.requirement)

        return template

    def validate_requirement_coverage(
        self, domain: str, covered_areas: List[str]
    ) -> Dict[str, bool]:
        """Validate whether requirements are covered by provided areas.

        Args:
            domain: Business domain name
            covered_areas: List of areas that have been covered

        Returns:
            Dictionary mapping requirement IDs to coverage status
        """
        domain_reqs = self.get_domain_requirements(domain)
        coverage_status = {}

        for req in domain_reqs:
            # Simple keyword matching for now - could be enhanced with NLP
            requirement_covered = any(
                any(
                    keyword.lower() in area.lower()
                    for keyword in req.requirement.split()
                )
                for area in covered_areas
            )

            coverage_status[f"{req.domain}_{req.category}_{req.requirement[:20]}"] = (
                requirement_covered
            )

        return coverage_status
