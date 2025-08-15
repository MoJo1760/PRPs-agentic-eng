"""Intelligent questioning engine for extracting business requirements."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.business_concept import (
    BusinessConceptRequest,
    ConceptAnalysis,
    BusinessDomain,
    BusinessModel,
)
from ..models.questionnaire import (
    Question,
    QuestionType,
    QuestionCategory,
    QuestionnaireSession,
    QuestionnaireResponse,
    QuestionnaireGenerationRequest,
)
from ..models.gap_analysis import KnowledgeGap, GapAnalysisResult

logger = logging.getLogger(__name__)


class QuestioningEngine:
    """Generates intelligent, context-aware questions for business concepts."""

    def __init__(self, ai_client=None, max_questions: int = 15):
        """Initialize questioning engine.

        Args:
            ai_client: AI service client for generating questions
            max_questions: Maximum questions per questionnaire
        """
        self.ai_client = ai_client
        self.max_questions = max_questions
        self._domain_question_templates = self._load_domain_templates()

    def _load_domain_templates(self) -> Dict[BusinessDomain, List[Dict]]:
        """Load pre-defined question templates for different business domains."""
        return {
            BusinessDomain.SAAS: [
                {
                    "category": QuestionCategory.BUSINESS_MODEL,
                    "text": "What subscription tiers do you envision? (Free, Basic, Pro, Enterprise?)",
                    "type": QuestionType.TEXT,
                    "priority": 2,
                },
                {
                    "category": QuestionCategory.TARGET_MARKET,
                    "text": "Are you targeting small businesses, enterprises, or individual users?",
                    "type": QuestionType.SINGLE_SELECT,
                    "options": [
                        "Small businesses (1-50 employees)",
                        "Mid-market (51-500 employees)",
                        "Enterprise (500+ employees)",
                        "Individual consumers",
                        "Mixed target",
                    ],
                    "priority": 1,
                },
                {
                    "category": QuestionCategory.TECHNICAL_REQUIREMENTS,
                    "text": "Do you need real-time features (live chat, notifications, collaboration)?",
                    "type": QuestionType.BOOLEAN,
                    "priority": 3,
                },
            ],
            BusinessDomain.E_COMMERCE: [
                {
                    "category": QuestionCategory.BUSINESS_MODEL,
                    "text": "Will you sell physical products, digital products, or services?",
                    "type": QuestionType.SINGLE_SELECT,
                    "options": [
                        "Physical products only",
                        "Digital products only",
                        "Services only",
                        "Mix of physical and digital",
                        "All three",
                    ],
                    "priority": 1,
                },
                {
                    "category": QuestionCategory.TECHNICAL_REQUIREMENTS,
                    "text": "Do you need inventory management, order tracking, and payment processing?",
                    "type": QuestionType.BOOLEAN,
                    "priority": 2,
                },
            ],
            BusinessDomain.MOBILE_APP: [
                {
                    "category": QuestionCategory.TECHNICAL_REQUIREMENTS,
                    "text": "Do you need native iOS/Android apps or is a web app sufficient?",
                    "type": QuestionType.SINGLE_SELECT,
                    "options": [
                        "Native iOS and Android",
                        "Native iOS only",
                        "Native Android only",
                        "Progressive Web App (PWA)",
                        "React Native/Flutter cross-platform",
                    ],
                    "priority": 1,
                },
                {
                    "category": QuestionCategory.USER_EXPERIENCE,
                    "text": "Do you need offline functionality for your mobile app?",
                    "type": QuestionType.BOOLEAN,
                    "priority": 2,
                },
            ],
        }

    async def analyze_business_concept(
        self, concept: BusinessConceptRequest
    ) -> ConceptAnalysis:
        """Analyze business concept to understand complexity and generate insights."""
        # Basic complexity analysis based on description and requirements
        complexity_indicators = [
            len(concept.description) > 500,  # Detailed description
            concept.technical_constraints is not None,  # Has constraints
            concept.existing_competitors is not None,  # Market awareness
            concept.domain
            in [BusinessDomain.FINTECH, BusinessDomain.HEALTHCARE],  # Complex domains
        ]

        complexity_score = sum(complexity_indicators) * 2.5  # Scale to 0-10

        # Feasibility assessment
        feasibility_factors = [
            concept.business_model is not None,  # Clear monetization
            concept.target_users is not None,  # Defined target market
            len(concept.description.split()) > 50,  # Detailed description
            concept.domain != BusinessDomain.OTHER,  # Specific domain
        ]

        feasibility_score = sum(feasibility_factors) * 2.5

        # Market potential (simplified heuristic)
        market_indicators = [
            concept.domain
            in [BusinessDomain.SAAS, BusinessDomain.E_COMMERCE, BusinessDomain.FINTECH],
            concept.business_model
            in [BusinessModel.SUBSCRIPTION, BusinessModel.MARKETPLACE],
            "small business" in concept.description.lower(),
            "automation" in concept.description.lower()
            or "ai" in concept.description.lower(),
        ]

        market_potential_score = sum(market_indicators) * 2.5

        # Generate insights
        technical_challenges = self._identify_technical_challenges(concept)
        market_opportunities = self._identify_market_opportunities(concept)
        mvp_features = self._suggest_mvp_features(concept)
        similar_products = self._find_similar_products(concept)

        return ConceptAnalysis(
            concept_id=f"concept_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            complexity_score=min(complexity_score, 10.0),
            feasibility_score=min(feasibility_score, 10.0),
            market_potential_score=min(market_potential_score, 10.0),
            technical_challenges=technical_challenges,
            market_opportunities=market_opportunities,
            recommended_mvp_features=mvp_features,
            similar_successful_products=similar_products,
            analysis_timestamp=datetime.utcnow(),
        )

    def _identify_technical_challenges(
        self, concept: BusinessConceptRequest
    ) -> List[str]:
        """Identify potential technical challenges based on concept."""
        challenges = []

        if concept.domain == BusinessDomain.FINTECH:
            challenges.extend(
                [
                    "Payment processing and PCI compliance",
                    "Financial data security and encryption",
                    "Regulatory compliance (KYC/AML)",
                ]
            )

        if concept.domain == BusinessDomain.HEALTHCARE:
            challenges.extend(
                [
                    "HIPAA compliance for patient data",
                    "Medical device integration",
                    "Clinical workflow optimization",
                ]
            )

        if "real-time" in concept.description.lower():
            challenges.append("Real-time data synchronization and WebSocket management")

        if (
            "scale" in concept.description.lower()
            or "million" in concept.description.lower()
        ):
            challenges.append("High-scale architecture and database optimization")

        if concept.domain == BusinessDomain.MOBILE_APP:
            challenges.extend(
                [
                    "Cross-platform compatibility",
                    "App store approval process",
                    "Push notification systems",
                ]
            )

        return challenges[:5]  # Limit to top 5

    def _identify_market_opportunities(
        self, concept: BusinessConceptRequest
    ) -> List[str]:
        """Identify market opportunities."""
        opportunities = []

        if "small business" in concept.description.lower():
            opportunities.append("Large underserved small business market")

        if concept.domain == BusinessDomain.AI_ML:
            opportunities.append("Growing AI adoption across industries")

        if "automation" in concept.description.lower():
            opportunities.append("Increasing demand for business process automation")

        if concept.business_model == BusinessModel.SUBSCRIPTION:
            opportunities.append(
                "Recurring revenue model with high customer lifetime value"
            )

        return opportunities[:3]

    def _suggest_mvp_features(self, concept: BusinessConceptRequest) -> List[str]:
        """Suggest MVP features based on concept."""
        mvp_features = ["User authentication and basic profile management"]

        if concept.domain == BusinessDomain.SAAS:
            mvp_features.extend(
                [
                    "Core workflow or task management",
                    "Basic dashboard with key metrics",
                    "Simple subscription management",
                ]
            )

        if concept.domain == BusinessDomain.E_COMMERCE:
            mvp_features.extend(
                [
                    "Product catalog and search",
                    "Shopping cart and checkout",
                    "Order management system",
                ]
            )

        if concept.domain == BusinessDomain.MOBILE_APP:
            mvp_features.extend(
                [
                    "Core mobile functionality",
                    "Offline data storage",
                    "Push notifications",
                ]
            )

        return mvp_features[:5]

    def _find_similar_products(self, concept: BusinessConceptRequest) -> List[str]:
        """Find similar successful products for reference."""
        # This would typically use web search or a database of products
        similar_products = []

        if concept.domain == BusinessDomain.SAAS:
            if "project" in concept.description.lower():
                similar_products.extend(["Asana", "Monday.com", "Clickup"])
            elif "communication" in concept.description.lower():
                similar_products.extend(["Slack", "Microsoft Teams", "Discord"])

        if concept.domain == BusinessDomain.E_COMMERCE:
            similar_products.extend(["Shopify", "WooCommerce", "Squarespace Commerce"])

        return similar_products[:3]

    async def generate_questions(
        self, request: QuestionnaireGenerationRequest, concept: BusinessConceptRequest
    ) -> List[Question]:
        """Generate intelligent questions based on business concept."""
        questions = []

        # Start with domain-specific template questions
        domain_templates = self._domain_question_templates.get(concept.domain, [])

        for i, template in enumerate(domain_templates[: request.max_questions // 2]):
            question = Question(
                id=f"q_{concept.domain.value}_{i + 1}",
                text=template["text"],
                type=QuestionType(template["type"]),
                category=QuestionCategory(template["category"]),
                options=template.get("options"),
                priority=template.get("priority", 5),
            )
            questions.append(question)

        # Add generic business questions
        generic_questions = [
            Question(
                id="q_generic_1",
                text="What is the primary problem your solution solves for users?",
                type=QuestionType.TEXT,
                category=QuestionCategory.BUSINESS_MODEL,
                priority=1,
            ),
            Question(
                id="q_generic_2",
                text="How will users discover and access your solution?",
                type=QuestionType.TEXT,
                category=QuestionCategory.TARGET_MARKET,
                priority=2,
            ),
            Question(
                id="q_generic_3",
                text="What key metrics will measure your solution's success?",
                type=QuestionType.TEXT,
                category=QuestionCategory.BUSINESS_MODEL,
                priority=3,
            ),
            Question(
                id="q_generic_4",
                text="Do you need user roles and permissions (admin, user, etc.)?",
                type=QuestionType.BOOLEAN,
                category=QuestionCategory.USER_EXPERIENCE,
                priority=4,
            ),
            Question(
                id="q_generic_5",
                text="What integrations with other tools/services do you need?",
                type=QuestionType.TEXT,
                category=QuestionCategory.INTEGRATION,
                priority=5,
            ),
        ]

        # Add generic questions to fill up to max_questions
        remaining_slots = request.max_questions - len(questions)
        questions.extend(generic_questions[:remaining_slots])

        # Sort by priority and return
        return sorted(questions, key=lambda q: q.priority)[: request.max_questions]

    def create_questionnaire_session(
        self, concept_id: str, questions: List[Question]
    ) -> QuestionnaireSession:
        """Create a new questionnaire session."""
        session_id = (
            f"session_{concept_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )

        return QuestionnaireSession(
            session_id=session_id,
            concept_id=concept_id,
            questions=questions,
            responses=[],
            current_question_index=0,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )

    def get_next_question(self, session: QuestionnaireSession) -> Optional[Question]:
        """Get the next question in the session."""
        return session.next_question

    def add_response(
        self, session: QuestionnaireSession, response: QuestionnaireResponse
    ) -> bool:
        """Add a response to the questionnaire session."""
        try:
            # Validate response
            question = next(
                (q for q in session.questions if q.id == response.question_id), None
            )

            if not question:
                logger.warning(f"Question {response.question_id} not found in session")
                return False

            # Add response to session
            session.add_response(response)

            logger.info(
                f"Added response for question {response.question_id} in session {session.session_id}. "
                f"Completion: {session.completion_percentage:.1f}%"
            )

            return True

        except Exception as e:
            logger.error(f"Error adding response: {e}")
            return False

    def is_questionnaire_complete(self, session: QuestionnaireSession) -> bool:
        """Check if questionnaire is complete."""
        return session.is_complete

    def get_questionnaire_summary(
        self, session: QuestionnaireSession
    ) -> Dict[str, Any]:
        """Generate summary of questionnaire responses."""
        if not session.responses:
            return {"status": "no_responses", "summary": "No responses collected yet"}

        # Categorize responses
        categorized_responses = {}
        for response in session.responses:
            question = next(
                (q for q in session.questions if q.id == response.question_id), None
            )
            if question:
                if question.category.value not in categorized_responses:
                    categorized_responses[question.category.value] = []

                categorized_responses[question.category.value].append(
                    {
                        "question": question.text,
                        "answer": response.answer,
                        "confidence": response.confidence_score,
                    }
                )

        return {
            "status": "complete" if session.is_complete else "partial",
            "completion_percentage": session.completion_percentage,
            "total_responses": len(session.responses),
            "categorized_responses": categorized_responses,
            "session_duration_minutes": (
                datetime.utcnow() - session.started_at
            ).total_seconds()
            / 60,
        }

    async def generate_gap_targeted_questions(
        self,
        gaps: List[KnowledgeGap],
        concept: BusinessConceptRequest,
        max_questions: int = 10,
    ) -> List[Question]:
        """Generate questions specifically targeting identified knowledge gaps.

        Args:
            gaps: List of knowledge gaps to target
            concept: Business concept being researched
            max_questions: Maximum number of questions to generate

        Returns:
            List of targeted questions addressing the gaps
        """
        targeted_questions = []

        # Sort gaps by priority and confidence score
        prioritized_gaps = sorted(
            gaps,
            key=lambda g: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[g.priority],
                g.confidence_score,
            ),
            reverse=True,
        )

        question_id_counter = 1

        for gap in prioritized_gaps[:max_questions]:
            # Generate question based on gap category and description
            question_text = self._generate_question_for_gap(gap, concept)
            
            if question_text:
                question_category = self._map_gap_category_to_question_category(
                    gap.category
                )
                question_type = self._determine_question_type_for_gap(gap)

                question = Question(
                    id=f"gap_q_{question_id_counter}_{gap.id}",
                    text=question_text,
                    type=question_type,
                    category=question_category,
                    options=self._get_question_options_for_gap(gap, question_type),
                    priority={"critical": 1, "high": 2, "medium": 3, "low": 4}[
                        gap.priority
                    ],
                    metadata={
                        "gap_id": gap.id,
                        "gap_category": gap.category,
                        "gap_description": gap.description,
                        "confidence_score": gap.confidence_score,
                    },
                )

                targeted_questions.append(question)
                question_id_counter += 1

        logger.info(
            f"Generated {len(targeted_questions)} gap-targeted questions from {len(gaps)} gaps"
        )

        return targeted_questions

    def _get_gap_question_templates(self) -> Dict[str, List[str]]:
        """Get question templates for different gap categories."""
        return {
            "business_model": [
                "How do you plan to monetize this solution?",
                "What pricing strategy will you use?",
                "What is your revenue model?",
                "How will customers pay for your service?",
                "What subscription tiers do you envision?",
            ],
            "technical_requirements": [
                "What are the key technical features needed?",
                "What performance requirements must be met?",
                "What security measures are required?",
                "What integrations are necessary?",
                "What scalability requirements do you have?",
            ],
            "user_experience": [
                "Who are your primary users?",
                "What devices will users access this from?",
                "What is the main user workflow?",
                "What accessibility requirements do you have?",
                "How should users navigate the system?",
            ],
            "integration": [
                "What third-party services need integration?",
                "What APIs will you need to connect to?",
                "What data sources will you use?",
                "What external tools must work with your solution?",
                "What webhook or notification systems are needed?",
            ],
            "validation": [
                "How will you test this solution?",
                "What quality metrics will you track?",
                "What monitoring is needed?",
                "How will you handle errors?",
                "What logging requirements do you have?",
            ],
            "deployment": [
                "Where will this be hosted?",
                "What deployment strategy will you use?",
                "What infrastructure requirements do you have?",
                "What CI/CD processes are needed?",
                "What scaling approach will you take?",
            ],
            "goal_definition": [
                "What specific problem does this solve?",
                "What are the success criteria?",
                "What are the key objectives?",
                "What outcomes are expected?",
                "How will success be measured?",
            ],
        }

    def _generate_question_for_gap(
        self, gap: KnowledgeGap, concept: BusinessConceptRequest
    ) -> str:
        """Generate a specific question text for a knowledge gap."""
        templates = self._get_gap_question_templates().get(gap.category, [])
        
        if templates:
            # Use the first template as base and customize it
            base_question = templates[0]
            
            # Customize based on gap description
            if "Missing or insufficient information about:" in gap.description:
                specific_info = gap.description.replace(
                    "Missing or insufficient information about:", ""
                ).strip()
                return f"Can you provide details about {specific_info}?"
            
            # Customize based on domain
            domain_context = ""
            if concept.domain:
                domain_context = f" for your {concept.domain.value} solution"
            
            return base_question.replace("this", concept.title).replace("your solution", f"your {concept.title}") + domain_context
        
        # Fallback generic question
        return f"Can you provide more information about {gap.category.replace('_', ' ')} for {concept.title}?"

    def _map_gap_category_to_question_category(self, gap_category: str) -> QuestionCategory:
        """Map gap category to questionnaire question category."""
        category_mapping = {
            "business_model": QuestionCategory.BUSINESS_MODEL,
            "technical_requirements": QuestionCategory.TECHNICAL_REQUIREMENTS,
            "user_experience": QuestionCategory.USER_EXPERIENCE,
            "integration": QuestionCategory.INTEGRATION,
            "validation": QuestionCategory.VALIDATION,
            "deployment": QuestionCategory.TECHNICAL_REQUIREMENTS,  # Map to closest match
            "goal_definition": QuestionCategory.BUSINESS_MODEL,  # Map to closest match
        }
        
        return category_mapping.get(gap_category, QuestionCategory.OTHER)

    def _determine_question_type_for_gap(self, gap: KnowledgeGap) -> QuestionType:
        """Determine the most appropriate question type for a gap."""
        # Simple heuristics based on gap category and description
        if gap.category in ["business_model", "technical_requirements"]:
            if any(
                word in gap.description.lower()
                for word in ["yes", "no", "boolean", "true", "false", "do you need"]
            ):
                return QuestionType.BOOLEAN
            elif any(
                word in gap.description.lower()
                for word in ["choose", "select", "option", "tier", "model"]
            ):
                return QuestionType.SINGLE_SELECT
        
        # Default to text for detailed explanations
        return QuestionType.TEXT

    def _get_question_options_for_gap(
        self, gap: KnowledgeGap, question_type: QuestionType
    ) -> Optional[List[str]]:
        """Get predefined options for single/multi-select questions targeting gaps."""
        if question_type not in [QuestionType.SINGLE_SELECT, QuestionType.MULTI_SELECT]:
            return None

        # Options based on gap category
        if gap.category == "business_model":
            return [
                "Subscription/SaaS",
                "One-time purchase",
                "Freemium",
                "Commission/Marketplace",
                "Advertising",
                "Usage-based pricing",
                "Not yet determined",
            ]
        elif gap.category == "technical_requirements":
            return [
                "Web application",
                "Mobile application",
                "Desktop application",
                "API/Backend service",
                "Integration/Plugin",
                "Multiple platforms",
            ]
        elif gap.category == "user_experience":
            return [
                "Individual consumers",
                "Small businesses",
                "Medium businesses",
                "Enterprise",
                "Developers/Technical users",
                "Non-technical users",
                "Mixed audience",
            ]
        elif gap.category == "integration":
            return [
                "Payment gateways",
                "Email services",
                "Cloud storage",
                "Analytics tools",
                "CRM systems",
                "Marketing tools",
                "Social media",
                "No integrations needed",
            ]

        return None

    async def enhance_questionnaire_with_gaps(
        self,
        existing_questions: List[Question],
        gap_analysis: GapAnalysisResult,
        concept: BusinessConceptRequest,
        max_additional_questions: int = 5,
    ) -> List[Question]:
        """Enhance existing questionnaire with gap-targeted questions.

        Args:
            existing_questions: Current questions in the questionnaire
            gap_analysis: Analysis of knowledge gaps
            concept: Business concept being researched
            max_additional_questions: Maximum additional questions to add

        Returns:
            Enhanced list of questions including gap-targeted ones
        """
        # Get high-priority gaps not already covered by existing questions
        uncovered_gaps = self._find_uncovered_gaps(
            existing_questions, gap_analysis.identified_gaps
        )

        # Generate additional questions for uncovered gaps
        additional_questions = await self.generate_gap_targeted_questions(
            uncovered_gaps, concept, max_additional_questions
        )

        # Combine and deduplicate
        all_questions = existing_questions + additional_questions
        
        # Remove duplicate questions (same text)
        seen_texts = set()
        unique_questions = []
        for question in all_questions:
            if question.text not in seen_texts:
                unique_questions.append(question)
                seen_texts.add(question.text)

        # Sort by priority
        return sorted(unique_questions, key=lambda q: q.priority)

    def _find_uncovered_gaps(
        self, existing_questions: List[Question], gaps: List[KnowledgeGap]
    ) -> List[KnowledgeGap]:
        """Find gaps that are not already covered by existing questions."""
        # Get categories covered by existing questions
        covered_categories = set()
        for question in existing_questions:
            covered_categories.add(question.category.value)

        # Find gaps in categories not covered or high-priority gaps
        uncovered_gaps = []
        for gap in gaps:
            if (
                gap.category not in covered_categories
                or gap.priority in ["critical", "high"]
            ):
                uncovered_gaps.append(gap)

        return uncovered_gaps

    async def generate_follow_up_questions(
        self,
        previous_responses: List[QuestionnaireResponse],
        gap_analysis: GapAnalysisResult,
        concept: BusinessConceptRequest,
        max_questions: int = 3,
    ) -> List[Question]:
        """Generate follow-up questions based on previous responses and remaining gaps.

        Args:
            previous_responses: Previous questionnaire responses
            gap_analysis: Current gap analysis
            concept: Business concept
            max_questions: Maximum follow-up questions

        Returns:
            List of follow-up questions
        """
        # Analyze responses to identify areas needing clarification
        unclear_responses = []
        for response in previous_responses:
            if (
                response.confidence_score < 0.7
                or len(response.answer.strip()) < 20  # Very brief answers
            ):
                unclear_responses.append(response)

        # Generate clarifying questions for unclear responses
        follow_up_questions = []
        question_counter = 1

        for response in unclear_responses[:max_questions]:
            # Find the original question
            original_question_id = response.question_id
            
            follow_up_text = f"Can you provide more details about your previous answer regarding '{response.answer[:50]}...'?"
            
            follow_up = Question(
                id=f"followup_{question_counter}_{original_question_id}",
                text=follow_up_text,
                type=QuestionType.TEXT,
                category=QuestionCategory.OTHER,
                priority=2,  # High priority for clarification
                metadata={
                    "original_question_id": original_question_id,
                    "follow_up_type": "clarification",
                    "original_confidence": response.confidence_score,
                },
            )
            
            follow_up_questions.append(follow_up)
            question_counter += 1

        logger.info(f"Generated {len(follow_up_questions)} follow-up questions")
        
        return follow_up_questions
