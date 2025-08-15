"""PRP generation service using templates and research context."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

from ..models.business_concept import BusinessConceptRequest
from ..models.questionnaire import QuestionnaireSession
from .research_service import ResearchContext

logger = logging.getLogger(__name__)


@dataclass
class GeneratedPRP:
    """Generated PRP with metadata."""
    id: str
    title: str
    content: str
    quality_metrics: Dict[str, float]
    validation_commands: List[str]
    estimated_complexity: str  # "simple", "moderate", "complex"
    template_used: str
    generation_timestamp: datetime


class PRPGenerator:
    """Generates comprehensive PRPs using templates and research context."""
    
    def __init__(self, prp_templates_path: str = "PRPs/templates", min_quality_score: float = 8.0):
        """Initialize PRP generator.
        
        Args:
            prp_templates_path: Path to PRP templates directory
            min_quality_score: Minimum quality score for generated PRPs
        """
        self.templates_path = Path(prp_templates_path)
        self.min_quality_score = min_quality_score
        self._templates_cache: Dict[str, str] = {}
        self._load_templates()
        
    def _load_templates(self):
        """Load PRP templates from templates directory."""
        try:
            if self.templates_path.exists():
                for template_file in self.templates_path.glob("*.md"):
                    template_name = template_file.stem
                    self._templates_cache[template_name] = template_file.read_text()
                    logger.info(f"Loaded PRP template: {template_name}")
            else:
                logger.warning(f"Templates path does not exist: {self.templates_path}")
                # Load fallback template
                self._templates_cache["prp_base"] = self._get_fallback_template()
                
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            self._templates_cache["prp_base"] = self._get_fallback_template()
    
    async def generate_prp(
        self,
        concept: BusinessConceptRequest,
        questionnaire_session: QuestionnaireSession,
        research_context: ResearchContext,
        template_name: str = "prp_base"
    ) -> GeneratedPRP:
        """Generate comprehensive PRP from concept, questionnaire, and research.
        
        Args:
            concept: Business concept request
            questionnaire_session: Completed questionnaire session  
            research_context: Research context from research service
            template_name: PRP template to use
            
        Returns:
            GeneratedPRP with content and quality metrics
        """
        logger.info(f"Generating PRP for concept: {concept.title}")
        
        # Get template
        template = self._templates_cache.get(template_name)
        if not template:
            logger.warning(f"Template {template_name} not found, using base template")
            template = self._templates_cache.get("prp_base", self._get_fallback_template())
        
        # Generate PRP content by populating template sections
        prp_content = await self._populate_prp_template(
            template, concept, questionnaire_session, research_context
        )
        
        # Assess quality
        quality_metrics = self._assess_prp_quality(prp_content, research_context)
        
        # Enhance if quality is below threshold
        if quality_metrics["overall_score"] < self.min_quality_score:
            logger.info(f"PRP quality {quality_metrics['overall_score']:.1f} below threshold, enhancing...")
            prp_content = await self._enhance_prp_content(
                prp_content, concept, research_context, quality_metrics
            )
            quality_metrics = self._assess_prp_quality(prp_content, research_context)
        
        # Extract validation commands
        validation_commands = self._extract_validation_commands(prp_content)
        
        # Determine complexity
        complexity = self._estimate_complexity(concept, questionnaire_session, research_context)
        
        # Generate unique ID
        prp_id = f"prp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{concept.domain.value if concept.domain else 'general'}"
        
        return GeneratedPRP(
            id=prp_id,
            title=f"{concept.title} - Implementation PRP",
            content=prp_content,
            quality_metrics=quality_metrics,
            validation_commands=validation_commands,
            estimated_complexity=complexity,
            template_used=template_name,
            generation_timestamp=datetime.utcnow()
        )
    
    async def _populate_prp_template(
        self,
        template: str,
        concept: BusinessConceptRequest,
        questionnaire_session: QuestionnaireSession,
        research_context: ResearchContext
    ) -> str:
        """Populate PRP template with generated content."""
        
        # Extract questionnaire insights
        questionnaire_summary = self._summarize_questionnaire_responses(questionnaire_session)
        
        # Generate each section
        sections = {
            "FEATURE_GOAL": self._generate_feature_goal(concept, questionnaire_summary),
            "DELIVERABLE": self._generate_deliverable(concept, questionnaire_summary),
            "SUCCESS_DEFINITION": self._generate_success_definition(concept, questionnaire_summary),
            "TARGET_USER": self._generate_target_user(concept, questionnaire_summary),
            "USE_CASE": self._generate_use_case(concept, questionnaire_summary),
            "USER_JOURNEY": self._generate_user_journey(concept, questionnaire_summary),
            "PAIN_POINTS": self._generate_pain_points(concept, questionnaire_summary),
            "WHY_SECTION": self._generate_why_section(concept, research_context),
            "WHAT_SECTION": self._generate_what_section(concept, questionnaire_summary),
            "SUCCESS_CRITERIA": self._generate_success_criteria(concept, questionnaire_summary),
            "CONTEXT_SECTION": self._generate_context_section(research_context),
            "IMPLEMENTATION_TASKS": self._generate_implementation_tasks(concept, research_context, questionnaire_summary),
            "VALIDATION_LOOP": self._generate_validation_loop(concept, research_context),
            "ANTI_PATTERNS": self._generate_anti_patterns(concept.domain.value if concept.domain else "general", research_context)
        }
        
        # Replace template placeholders
        populated_template = template
        for placeholder, content in sections.items():
            populated_template = populated_template.replace(f"[{placeholder}]", content)
            populated_template = populated_template.replace(f"{{{{{placeholder}}}}}", content)
        
        # Replace concept-specific placeholders
        populated_template = populated_template.replace("[CONCEPT_TITLE]", concept.title)
        populated_template = populated_template.replace("[CONCEPT_DESCRIPTION]", concept.description)
        populated_template = populated_template.replace("[BUSINESS_DOMAIN]", concept.domain.value if concept.domain else "general")
        populated_template = populated_template.replace("[BUSINESS_MODEL]", concept.business_model.value if concept.business_model else "not specified")
        
        return populated_template
    
    def _summarize_questionnaire_responses(self, session: QuestionnaireSession) -> Dict[str, Any]:
        """Summarize questionnaire responses by category."""
        summary = {
            "business_model": [],
            "target_market": [], 
            "technical_requirements": [],
            "user_experience": [],
            "monetization": [],
            "scalability": [],
            "integration": [],
            "compliance": []
        }
        
        for response in session.responses:
            question = next((q for q in session.questions if q.id == response.question_id), None)
            if question:
                category = question.category.value
                if category in summary:
                    summary[category].append({
                        "question": question.text,
                        "answer": response.answer,
                        "confidence": response.confidence_score
                    })
        
        return summary
    
    def _generate_feature_goal(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate feature goal section."""
        goal = f"Build a {concept.domain.value if concept.domain else 'software'} solution that {concept.description.lower()}"
        
        # Add specific goals from questionnaire
        if questionnaire_summary.get("business_model"):
            primary_goal = questionnaire_summary["business_model"][0]["answer"]
            goal += f"\n\n**Primary Business Goal**: {primary_goal}"
        
        return goal
    
    def _generate_deliverable(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate deliverable section.""" 
        deliverable = f"Production-ready {concept.domain.value if concept.domain else 'software'} application with:"
        
        features = [
            "Complete user authentication and authorization system",
            "Core business logic implementation",
            "Database design and implementation",
            "API endpoints for all major functions"
        ]
        
        # Add domain-specific deliverables
        if concept.domain and concept.domain.value == "saas":
            features.extend([
                "Multi-tenant architecture",
                "Subscription management system",
                "Admin dashboard"
            ])
        elif concept.domain and concept.domain.value == "e_commerce":
            features.extend([
                "Product catalog management",
                "Shopping cart and checkout",
                "Order processing system"
            ])
        
        return deliverable + "\n" + "\n".join(f"- {feature}" for feature in features)
    
    def _generate_success_definition(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate success definition."""
        return f"The {concept.title} application is complete when:\n" + \
               "- All core features are implemented and tested\n" + \
               "- API endpoints return correct responses\n" + \
               "- Database operations work correctly\n" + \
               "- Security measures are in place\n" + \
               "- Application passes all validation tests"
    
    def _generate_target_user(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate target user section."""
        if concept.target_users:
            return concept.target_users
        
        # Extract from questionnaire
        target_market_responses = questionnaire_summary.get("target_market", [])
        if target_market_responses:
            return target_market_responses[0]["answer"]
        
        # Default based on domain
        domain_users = {
            "saas": "Business professionals and teams who need workflow automation",
            "e_commerce": "Online shoppers and merchants selling products",
            "mobile_app": "Mobile device users seeking convenient access to services",
            "fintech": "Individuals and businesses managing financial transactions"
        }
        
        return domain_users.get(concept.domain.value if concept.domain else "general", "End users seeking digital solutions")
    
    def _generate_use_case(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate primary use case."""
        return f"Users access the {concept.title} to {concept.description.lower().replace(concept.title.lower(), 'the solution')}"
    
    def _generate_user_journey(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate user journey steps."""
        journey_steps = [
            "User discovers the application through marketing or referral",
            "User signs up and creates an account",
            "User completes onboarding and profile setup",
            "User begins using core features for their primary use case",
            "User integrates the solution into their regular workflow",
            "User potentially upgrades to premium features or refers others"
        ]
        
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(journey_steps))
    
    def _generate_pain_points(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate pain points addressed."""
        pain_points = [
            "Manual processes that could be automated",
            "Lack of centralized data and insights", 
            "Time-consuming repetitive tasks",
            "Poor user experience with existing solutions"
        ]
        
        # Add domain-specific pain points
        if concept.domain:
            domain_pains = {
                "saas": ["Difficulty collaborating across teams", "Limited reporting and analytics"],
                "e_commerce": ["Complex inventory management", "Cart abandonment issues"],
                "mobile_app": ["Limited mobile access to services", "Poor offline functionality"]
            }
            pain_points.extend(domain_pains.get(concept.domain.value, []))
        
        return "\n".join(f"- {pain}" for pain in pain_points[:4])
    
    def _generate_why_section(self, concept: BusinessConceptRequest, research_context: ResearchContext) -> str:
        """Generate why section with business value."""
        why_points = [
            f"**Market Opportunity**: {research_context.domain_overview[:200]}...",
            f"**User Value**: Solves key pain points in {concept.domain.value if concept.domain else 'the target'} domain",
            f"**Business Model**: {concept.business_model.value if concept.business_model else 'Scalable revenue'} approach with growth potential"
        ]
        
        # Add competitive advantage from research
        if research_context.competitor_analysis:
            why_points.append(f"**Competitive Advantage**: Improvements over existing solutions like {', '.join(research_context.competitor_analysis[:2])}")
        
        return "\n".join(why_points)
    
    def _generate_what_section(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate what section with technical requirements."""
        what_content = f"**Core Functionality**: {concept.description}\n\n"
        
        # Add technical requirements from questionnaire
        tech_requirements = questionnaire_summary.get("technical_requirements", [])
        if tech_requirements:
            what_content += "**Technical Requirements**:\n"
            for req in tech_requirements[:3]:
                what_content += f"- {req['answer']}\n"
            what_content += "\n"
        
        # Add user experience requirements
        ux_requirements = questionnaire_summary.get("user_experience", [])
        if ux_requirements:
            what_content += "**User Experience Requirements**:\n"
            for ux in ux_requirements[:3]:
                what_content += f"- {ux['answer']}\n"
        
        return what_content
    
    def _generate_success_criteria(self, concept: BusinessConceptRequest, questionnaire_summary: Dict) -> str:
        """Generate success criteria checklist."""
        criteria = [
            "All API endpoints respond correctly with proper status codes",
            "Database operations (CRUD) work for all entities", 
            "User authentication and authorization function properly",
            "Core business logic produces expected results",
            "Application handles error cases gracefully"
        ]
        
        # Add domain-specific criteria
        if concept.domain:
            domain_criteria = {
                "saas": ["Multi-tenant data isolation works correctly", "Subscription billing processes payments"],
                "e_commerce": ["Order processing completes successfully", "Payment processing is secure"],
                "mobile_app": ["Mobile API responses are optimized", "Offline functionality works correctly"]
            }
            criteria.extend(domain_criteria.get(concept.domain.value, []))
        
        return "\n".join(f"- [ ] {criterion}" for criterion in criteria[:6])
    
    def _generate_context_section(self, research_context: ResearchContext) -> str:
        """Generate all needed context section."""
        context_content = "### Documentation & References\n\n```yaml\n"
        
        # Add official documentation links with priority
        for i, link in enumerate(research_context.official_documentation_links[:3]):
            context_content += f"- url: {link}\n"
            context_content += "  why: Official documentation for implementation patterns and best practices\n"
            context_content += "  critical: Use official patterns to ensure compatibility and security\n\n"
        
        context_content += "```\n\n"
        
        # Add technical patterns
        if research_context.technical_patterns:
            context_content += "### Technical Patterns to Follow\n\n"
            for pattern in research_context.technical_patterns[:3]:
                context_content += f"- **Pattern**: {pattern}\n"
            context_content += "\n"
        
        # Add best practices
        if research_context.best_practices:
            context_content += "### Best Practices\n\n"
            for practice in research_context.best_practices[:3]:
                context_content += f"- {practice}\n"
            context_content += "\n"
        
        # Add common challenges
        if research_context.common_challenges:
            context_content += "### Known Challenges\n\n```python\n"
            for challenge in research_context.common_challenges[:3]:
                context_content += f"# CHALLENGE: {challenge}\n"
            context_content += "```\n"
        
        return context_content
    
    def _generate_implementation_tasks(
        self, 
        concept: BusinessConceptRequest, 
        research_context: ResearchContext,
        questionnaire_summary: Dict
    ) -> str:
        """Generate implementation tasks ordered by dependencies."""
        
        base_tasks = [
            {
                "task": "CREATE project structure and configuration",
                "details": [
                    "IMPLEMENT: Project setup with proper directory structure",
                    "FOLLOW pattern: Standard project layout for the chosen framework",
                    "NAMING: Clear, consistent naming conventions",
                    "PLACEMENT: Root directory with proper organization"
                ]
            },
            {
                "task": "CREATE data models",
                "details": [
                    "IMPLEMENT: Database models for all core entities",
                    "FOLLOW pattern: ORM best practices with proper relationships",
                    "NAMING: Descriptive model and field names",
                    "DEPENDENCIES: Database setup and migrations"
                ]
            },
            {
                "task": "CREATE API endpoints",
                "details": [
                    "IMPLEMENT: RESTful API endpoints for all operations",
                    "FOLLOW pattern: REST conventions with proper status codes",
                    "NAMING: RESTful URL patterns",
                    "DEPENDENCIES: Data models and validation"
                ]
            },
            {
                "task": "CREATE authentication system",
                "details": [
                    "IMPLEMENT: User registration, login, and session management",
                    "FOLLOW pattern: Secure authentication with proper token handling",
                    "NAMING: Clear auth endpoint naming",
                    "SECURITY: Password hashing and session security"
                ]
            },
            {
                "task": "CREATE business logic services",
                "details": [
                    "IMPLEMENT: Core business logic and workflows",
                    "FOLLOW pattern: Service layer separation",
                    "NAMING: Descriptive service method names",
                    "DEPENDENCIES: Data models and API layer"
                ]
            }
        ]
        
        # Add domain-specific tasks
        if concept.domain:
            if concept.domain.value == "saas":
                base_tasks.append({
                    "task": "CREATE multi-tenant architecture",
                    "details": [
                        "IMPLEMENT: Tenant isolation and data separation",
                        "FOLLOW pattern: Schema-based or database-based tenancy",
                        "SECURITY: Ensure tenant data isolation"
                    ]
                })
            elif concept.domain.value == "e_commerce":
                base_tasks.append({
                    "task": "CREATE order processing system",
                    "details": [
                        "IMPLEMENT: Cart, checkout, and order management",
                        "FOLLOW pattern: Order state machine",
                        "INTEGRATION: Payment gateway integration"
                    ]
                })
        
        # Format tasks
        formatted_tasks = "```yaml\n"
        for i, task in enumerate(base_tasks[:6], 1):
            formatted_tasks += f"Task {i}: {task['task']}\n"
            for detail in task['details']:
                formatted_tasks += f"  - {detail}\n"
            formatted_tasks += "\n"
        formatted_tasks += "```"
        
        return formatted_tasks
    
    def _generate_validation_loop(self, concept: BusinessConceptRequest, research_context: ResearchContext) -> str:
        """Generate validation loop commands."""
        validation_content = "### Level 1: Syntax & Style (Immediate Feedback)\n\n```bash\n"
        validation_content += "# Run after each file creation - fix before proceeding\n"
        validation_content += "ruff check src/ --fix     # Auto-format and fix linting issues\n"
        validation_content += "mypy src/                 # Type checking\n"
        validation_content += "ruff format src/          # Ensure consistent formatting\n\n"
        validation_content += "# Expected: Zero errors. If errors exist, fix before proceeding.\n"
        validation_content += "```\n\n"
        
        validation_content += "### Level 2: Unit Tests (Component Validation)\n\n```bash\n"
        validation_content += "# Test each component as created\n"
        validation_content += "pytest tests/ -v\n"
        validation_content += "pytest tests/ --cov=src --cov-report=term-missing\n\n"
        validation_content += "# Expected: All tests pass with >85% coverage\n"
        validation_content += "```\n\n"
        
        validation_content += "### Level 3: Integration Testing (System Validation)\n\n```bash\n"
        validation_content += "# Application startup validation\n"
        validation_content += "python main.py &\n"
        validation_content += "sleep 5  # Allow startup time\n\n"
        validation_content += "# Health check validation\n"
        validation_content += "curl -f http://localhost:8000/health || echo 'Health check failed'\n\n"
        validation_content += "# API endpoint testing\n"
        validation_content += "curl -X POST http://localhost:8000/api/v1/test \\\n"
        validation_content += "  -H 'Content-Type: application/json' \\\n"
        validation_content += "  -d '{\"test\": \"data\"}' | jq .\n\n"
        validation_content += "# Expected: All endpoints respond correctly\n"
        validation_content += "```\n"
        
        return validation_content
    
    def _generate_anti_patterns(self, domain: str, research_context: ResearchContext) -> str:
        """Generate anti-patterns to avoid."""
        general_anti_patterns = [
            "❌ Don't skip input validation - validate all user inputs",
            "❌ Don't ignore error handling - implement comprehensive error responses", 
            "❌ Don't hardcode configuration values - use environment variables",
            "❌ Don't skip authentication - implement proper access controls"
        ]
        
        # Add domain-specific anti-patterns
        domain_anti_patterns = {
            "saas": [
                "❌ Don't mix tenant data - ensure proper data isolation",
                "❌ Don't skip subscription validation - verify user access levels"
            ],
            "e_commerce": [
                "❌ Don't store payment details - use secure payment processors",
                "❌ Don't skip inventory checks - prevent overselling"
            ],
            "mobile_app": [
                "❌ Don't ignore mobile constraints - optimize for mobile performance",
                "❌ Don't skip offline handling - implement proper offline support"
            ]
        }
        
        anti_patterns = general_anti_patterns + domain_anti_patterns.get(domain, [])
        return "\n".join(anti_patterns[:6])
    
    def _assess_prp_quality(self, prp_content: str, research_context: ResearchContext) -> Dict[str, float]:
        """Assess quality of generated PRP."""
        metrics = {}
        
        # Content completeness (0-10)
        required_sections = ["Goal", "Why", "What", "Implementation", "Validation"]
        present_sections = sum(1 for section in required_sections if section.lower() in prp_content.lower())
        metrics["content_completeness"] = (present_sections / len(required_sections)) * 10
        
        # Context richness (0-10) 
        context_indicators = len(research_context.official_documentation_links) + len(research_context.technical_patterns)
        metrics["context_richness"] = min(context_indicators * 1.5, 10.0)
        
        # Validation coverage (0-10)
        validation_keywords = ["test", "validate", "check", "curl", "pytest"]
        validation_count = sum(prp_content.lower().count(keyword) for keyword in validation_keywords)
        metrics["validation_coverage"] = min(validation_count * 0.5, 10.0)
        
        # Technical depth (0-10)
        technical_keywords = ["implement", "pattern", "security", "database", "api"]
        technical_count = sum(prp_content.lower().count(keyword) for keyword in technical_keywords)
        metrics["technical_depth"] = min(technical_count * 0.3, 10.0)
        
        # Overall score
        metrics["overall_score"] = sum(metrics.values()) / len(metrics)
        
        return metrics
    
    async def _enhance_prp_content(
        self, 
        prp_content: str, 
        concept: BusinessConceptRequest,
        research_context: ResearchContext,
        quality_metrics: Dict[str, float]
    ) -> str:
        """Enhance PRP content to improve quality."""
        enhanced_content = prp_content
        
        # Add more context if context richness is low
        if quality_metrics["context_richness"] < 7.0:
            additional_context = "\n\n### Additional Context\n\n"
            additional_context += f"**Research Quality Score**: {research_context.research_quality_score:.1f}/10\n\n"
            
            if research_context.recommended_technologies:
                additional_context += "**Recommended Technologies**:\n"
                for tech in research_context.recommended_technologies[:3]:
                    additional_context += f"- {tech}\n"
                additional_context += "\n"
            
            enhanced_content = enhanced_content.replace(
                "## Implementation Blueprint", 
                additional_context + "## Implementation Blueprint"
            )
        
        # Add more validation if validation coverage is low  
        if quality_metrics["validation_coverage"] < 7.0:
            additional_validation = "\n### Level 4: Business Logic Validation\n\n```bash\n"
            additional_validation += "# Domain-specific validation commands\n"
            
            if concept.domain:
                domain_validations = {
                    "saas": ["# Test tenant isolation", "# Validate subscription billing"],
                    "e_commerce": ["# Test order processing", "# Validate payment integration"],
                    "mobile_app": ["# Test mobile API responses", "# Validate offline functionality"]
                }
                
                domain_commands = domain_validations.get(concept.domain.value, ["# Test core business logic"])
                for command in domain_commands:
                    additional_validation += f"{command}\n"
            
            additional_validation += "```\n"
            
            # Insert before final checklist
            enhanced_content = enhanced_content.replace(
                "## Final Validation Checklist",
                additional_validation + "\n## Final Validation Checklist"
            )
        
        return enhanced_content
    
    def _extract_validation_commands(self, prp_content: str) -> List[str]:
        """Extract validation commands from PRP content."""
        commands = []
        
        # Find bash code blocks
        bash_blocks = re.findall(r'```bash\n(.*?)\n```', prp_content, re.DOTALL)
        
        for block in bash_blocks:
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('sleep'):
                    # Basic command validation
                    if any(cmd in line for cmd in ['pytest', 'ruff', 'mypy', 'curl', 'python']):
                        commands.append(line)
        
        return commands[:10]  # Limit to first 10 commands
    
    def _estimate_complexity(
        self,
        concept: BusinessConceptRequest,
        questionnaire_session: QuestionnaireSession, 
        research_context: ResearchContext
    ) -> str:
        """Estimate implementation complexity."""
        complexity_score = 0
        
        # Domain complexity
        domain_complexity = {
            "fintech": 3,
            "healthcare": 3,
            "saas": 2,
            "e_commerce": 2,
            "mobile_app": 1,
            "other": 1
        }
        complexity_score += domain_complexity.get(concept.domain.value if concept.domain else "other", 1)
        
        # Description complexity
        if len(concept.description) > 200:
            complexity_score += 1
        if "integration" in concept.description.lower():
            complexity_score += 1
        if "real-time" in concept.description.lower():
            complexity_score += 1
            
        # Questionnaire complexity
        complexity_score += min(len(questionnaire_session.responses) // 5, 2)
        
        # Research complexity
        complexity_score += min(len(research_context.common_challenges) // 2, 2)
        
        # Classify complexity
        if complexity_score <= 3:
            return "simple"
        elif complexity_score <= 6:
            return "moderate"
        else:
            return "complex"
    
    def _get_fallback_template(self) -> str:
        """Fallback PRP template when templates can't be loaded."""
        return '''name: "[CONCEPT_TITLE] - Implementation PRP"
description: |
  Implementation PRP for [CONCEPT_TITLE]

## Goal

**Feature Goal**: [FEATURE_GOAL]

**Deliverable**: [DELIVERABLE]

**Success Definition**: [SUCCESS_DEFINITION]

## User Persona

**Target User**: [TARGET_USER]

**Use Case**: [USE_CASE]

**User Journey**: [USER_JOURNEY]

**Pain Points Addressed**: [PAIN_POINTS]

## Why

[WHY_SECTION]

## What

[WHAT_SECTION]

### Success Criteria

[SUCCESS_CRITERIA]

## All Needed Context

[CONTEXT_SECTION]

## Implementation Blueprint

### Implementation Tasks

[IMPLEMENTATION_TASKS]

## Validation Loop

[VALIDATION_LOOP]

## Anti-Patterns to Avoid

[ANTI_PATTERNS]
'''