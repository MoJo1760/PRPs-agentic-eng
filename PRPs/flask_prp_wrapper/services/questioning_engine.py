"""Intelligent questioning engine for dynamic follow-up questions."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import json
from datetime import datetime

from ..models.business_concept import BusinessConceptRequest, BusinessDomain, BusinessModel
from ..models.questionnaire import (
    Question, QuestionType, QuestionPriority, QuestionnaireResponse,
    QuestionnaireSession, QuestionGenerationRequest
)

logger = logging.getLogger(__name__)


class QuestioningEngine:
    """Service for generating intelligent follow-up questions."""
    
    def __init__(self, max_questions_per_session: int = 15):
        self.max_questions_per_session = max_questions_per_session
        self._question_templates = self._load_question_templates()
        self._domain_specific_questions = self._load_domain_questions()
    
    async def create_initial_questionnaire(
        self, 
        concept: BusinessConceptRequest,
        session_id: str
    ) -> QuestionnaireSession:
        """Create initial questionnaire based on business concept."""
        
        logger.info(f"Creating initial questionnaire for concept: {concept.title}")
        
        # Analyze concept to determine question focus areas
        focus_areas = self._analyze_concept_gaps(concept)
        
        # Generate core questions based on concept analysis
        questions = []
        
        # Add domain-specific questions
        if concept.domain:
            domain_questions = self._get_domain_questions(concept.domain, concept)
            questions.extend(domain_questions[:5])  # Limit initial domain questions
        
        # Add business model questions
        if concept.business_model:
            model_questions = self._get_business_model_questions(concept.business_model, concept)
            questions.extend(model_questions[:3])
        
        # Add gap-filling questions based on missing information
        gap_questions = await self._generate_gap_filling_questions(concept, focus_areas)
        questions.extend(gap_questions[:7])
        
        # Sort questions by priority and order
        questions.sort(key=lambda q: (q.priority.value, q.order))
        
        # Create session
        session = QuestionnaireSession(
            session_id=session_id,
            concept_id=concept.title,  # Use title as concept ID for now
            questions=questions[:self.max_questions_per_session],
            total_questions=len(questions[:self.max_questions_per_session])
        )
        
        session.update_progress()
        
        logger.info(f"Generated {len(session.questions)} initial questions")
        return session
    
    async def generate_follow_up_questions(
        self,
        session: QuestionnaireSession,
        recent_responses: List[QuestionnaireResponse],
        max_questions: int = 5
    ) -> List[Question]:
        """Generate intelligent follow-up questions based on recent responses."""
        
        logger.info(f"Generating up to {max_questions} follow-up questions")
        
        if len(session.questions) >= self.max_questions_per_session:
            logger.info("Maximum questions per session reached")
            return []
        
        # Analyze recent responses for patterns and opportunities
        insights = self._analyze_responses(recent_responses, session)
        
        # Generate contextual questions based on insights
        follow_up_questions = []
        
        for insight in insights[:max_questions]:
            question = await self._generate_contextual_question(insight, session)
            if question:
                follow_up_questions.append(question)
        
        logger.info(f"Generated {len(follow_up_questions)} follow-up questions")
        return follow_up_questions
    
    def validate_response(
        self,
        question: Question,
        response: QuestionnaireResponse
    ) -> Tuple[bool, List[str]]:
        """Validate a questionnaire response against question requirements."""
        
        errors = []
        
        # Required field validation
        if question.required and not response.answer:
            errors.append("This question is required")
        
        if not response.answer:
            return len(errors) == 0, errors
        
        # Type-specific validation
        if question.question_type == QuestionType.EMAIL:
            if not self._is_valid_email(str(response.answer)):
                errors.append("Please enter a valid email address")
        
        elif question.question_type == QuestionType.URL:
            if not self._is_valid_url(str(response.answer)):
                errors.append("Please enter a valid URL")
        
        elif question.question_type == QuestionType.NUMBER:
            try:
                num_value = float(response.answer)
                if question.min_value is not None and num_value < question.min_value:
                    errors.append(f"Value must be at least {question.min_value}")
                if question.max_value is not None and num_value > question.max_value:
                    errors.append(f"Value must be at most {question.max_value}")
            except (ValueError, TypeError):
                errors.append("Please enter a valid number")
        
        elif question.question_type in [QuestionType.TEXT_SHORT, QuestionType.TEXT_LONG]:
            text_value = str(response.answer)
            if question.min_length and len(text_value) < question.min_length:
                errors.append(f"Response must be at least {question.min_length} characters")
            if question.max_length and len(text_value) > question.max_length:
                errors.append(f"Response must be no more than {question.max_length} characters")
        
        elif question.question_type == QuestionType.RATING:
            try:
                rating = float(response.answer)
                min_rating = question.min_value or 1
                max_rating = question.max_value or 10
                if rating < min_rating or rating > max_rating:
                    errors.append(f"Rating must be between {min_rating} and {max_rating}")
            except (ValueError, TypeError):
                errors.append("Please enter a valid rating")
        
        elif question.question_type in [QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE]:
            if question.options:
                if question.question_type == QuestionType.SINGLE_CHOICE:
                    if str(response.answer) not in question.options:
                        errors.append("Please select a valid option")
                else:  # MULTIPLE_CHOICE
                    if isinstance(response.answer, list):
                        invalid_options = [opt for opt in response.answer if opt not in question.options]
                        if invalid_options:
                            errors.append(f"Invalid options: {', '.join(invalid_options)}")
                    else:
                        errors.append("Multiple choice answers must be a list")
        
        return len(errors) == 0, errors
    
    def _analyze_concept_gaps(self, concept: BusinessConceptRequest) -> List[str]:
        """Analyze business concept to identify information gaps."""
        
        gaps = []
        
        if not concept.target_users:
            gaps.append("target_users")
        if not concept.business_model:
            gaps.append("business_model")
        if not concept.domain:
            gaps.append("domain")
        if not concept.key_features or len(concept.key_features) < 3:
            gaps.append("key_features")
        if not concept.technical_preferences:
            gaps.append("technical_preferences")
        if not concept.similar_products:
            gaps.append("competitive_landscape")
        
        # Check description depth
        if len(concept.description) < 100:
            gaps.append("detailed_requirements")
        
        return gaps
    
    def _get_domain_questions(
        self, 
        domain: BusinessDomain, 
        concept: BusinessConceptRequest
    ) -> List[Question]:
        """Get domain-specific questions."""
        
        domain_questions = self._domain_specific_questions.get(domain.value, [])
        questions = []
        
        for i, q_template in enumerate(domain_questions):
            question = Question(
                text=q_template["text"],
                question_type=QuestionType(q_template["type"]),
                priority=QuestionPriority(q_template.get("priority", "medium")),
                category=f"domain_{domain.value}",
                order=i,
                options=q_template.get("options"),
                required=q_template.get("required", False)
            )
            questions.append(question)
        
        return questions
    
    def _get_business_model_questions(
        self,
        business_model: BusinessModel,
        concept: BusinessConceptRequest
    ) -> List[Question]:
        """Get business model specific questions."""
        
        questions = []
        
        if business_model == BusinessModel.SUBSCRIPTION:
            questions.extend([
                Question(
                    text="What subscription tiers or pricing levels do you plan to offer?",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.HIGH,
                    category="business_model",
                    order=1,
                    required=True
                ),
                Question(
                    text="What features will differentiate each subscription tier?",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.HIGH,
                    category="business_model",
                    order=2
                )
            ])
        
        elif business_model == BusinessModel.MARKETPLACE:
            questions.extend([
                Question(
                    text="Who are the primary sellers/service providers on your marketplace?",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.CRITICAL,
                    category="business_model",
                    order=1,
                    required=True
                ),
                Question(
                    text="What commission structure do you plan to use?",
                    question_type=QuestionType.SINGLE_CHOICE,
                    priority=QuestionPriority.HIGH,
                    category="business_model",
                    order=2,
                    options=["Fixed percentage", "Tiered percentage", "Fixed fee", "Subscription-based", "Hybrid model"]
                )
            ])
        
        elif business_model == BusinessModel.FREEMIUM:
            questions.extend([
                Question(
                    text="What core features will be available in the free tier?",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.CRITICAL,
                    category="business_model",
                    order=1,
                    required=True
                ),
                Question(
                    text="What premium features will incentivize users to upgrade?",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.HIGH,
                    category="business_model",
                    order=2,
                    required=True
                )
            ])
        
        return questions
    
    async def _generate_gap_filling_questions(
        self,
        concept: BusinessConceptRequest,
        gaps: List[str]
    ) -> List[Question]:
        """Generate questions to fill identified information gaps."""
        
        questions = []
        
        for i, gap in enumerate(gaps):
            if gap == "target_users":
                questions.append(Question(
                    text="Who are your primary target users? Please describe their demographics, needs, and pain points.",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.CRITICAL,
                    category="target_audience",
                    order=i,
                    required=True,
                    min_length=50
                ))
            
            elif gap == "key_features":
                questions.append(Question(
                    text="What are the top 5 most important features your users need? List them in order of priority.",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.CRITICAL,
                    category="features",
                    order=i,
                    required=True,
                    min_length=100
                ))
            
            elif gap == "technical_preferences":
                questions.append(Question(
                    text="Do you have any technical preferences or constraints?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    priority=QuestionPriority.MEDIUM,
                    category="technical",
                    order=i,
                    options=[
                        "Specific programming language required",
                        "Must use certain cloud provider",
                        "Need mobile compatibility",
                        "Integration with existing systems",
                        "Performance/scalability requirements",
                        "Security/compliance requirements",
                        "No specific preferences"
                    ]
                ))
            
            elif gap == "competitive_landscape":
                questions.append(Question(
                    text="What existing products or services are similar to your idea? How will you differentiate?",
                    question_type=QuestionType.TEXT_LONG,
                    priority=QuestionPriority.HIGH,
                    category="competitive",
                    order=i,
                    required=True,
                    min_length=75
                ))
        
        return questions
    
    async def _generate_contextual_question(
        self,
        insight: Dict[str, Any],
        session: QuestionnaireSession
    ) -> Optional[Question]:
        """Generate a contextual follow-up question based on insights."""
        
        insight_type = insight.get("type")
        context = insight.get("context", {})
        
        if insight_type == "technical_depth_needed":
            return Question(
                text=f"You mentioned {context.get('technology')}. What specific features or integrations do you need with this technology?",
                question_type=QuestionType.TEXT_LONG,
                priority=QuestionPriority.MEDIUM,
                category="technical_detail",
                order=len(session.questions)
            )
        
        elif insight_type == "user_journey_unclear":
            return Question(
                text="Can you walk me through a typical user's journey from discovering your product to becoming a paying customer?",
                question_type=QuestionType.TEXT_LONG,
                priority=QuestionPriority.HIGH,
                category="user_experience",
                order=len(session.questions),
                required=True,
                min_length=100
            )
        
        elif insight_type == "scalability_concerns":
            return Question(
                text="What's your expected user growth in the first year, and what scale do you need to plan for?",
                question_type=QuestionType.SINGLE_CHOICE,
                priority=QuestionPriority.MEDIUM,
                category="scalability",
                order=len(session.questions),
                options=[
                    "< 1,000 users",
                    "1,000 - 10,000 users", 
                    "10,000 - 100,000 users",
                    "100,000 - 1M users",
                    "> 1M users",
                    "Unsure"
                ]
            )
        
        return None
    
    def _analyze_responses(
        self,
        responses: List[QuestionnaireResponse],
        session: QuestionnaireSession
    ) -> List[Dict[str, Any]]:
        """Analyze responses to generate insights for follow-up questions."""
        
        insights = []
        
        for response in responses:
            question = next((q for q in session.questions if q.id == response.question_id), None)
            if not question:
                continue
            
            answer_str = str(response.answer).lower()
            
            # Technical insights
            if any(tech in answer_str for tech in ['api', 'database', 'cloud', 'integration']):
                insights.append({
                    "type": "technical_depth_needed",
                    "context": {"technology": response.answer},
                    "priority": "medium"
                })
            
            # User experience insights
            if question.category == "target_audience" and len(answer_str) > 200:
                insights.append({
                    "type": "user_journey_unclear",
                    "context": {"user_description": response.answer},
                    "priority": "high"
                })
            
            # Scalability insights
            if any(scale in answer_str for scale in ['million', 'thousands', 'scale', 'growth']):
                insights.append({
                    "type": "scalability_concerns",
                    "context": {"scale_mention": response.answer},
                    "priority": "medium"
                })
        
        return insights
    
    def _load_question_templates(self) -> Dict[str, Any]:
        """Load question templates for different scenarios."""
        
        return {
            "technical": [
                {
                    "text": "What programming languages or frameworks do you prefer?",
                    "type": "multiple_choice",
                    "options": ["Python", "JavaScript", "Java", "C#", "Go", "Ruby", "PHP", "Other"]
                }
            ],
            "business": [
                {
                    "text": "What's your primary revenue model?",
                    "type": "single_choice", 
                    "options": ["Subscription", "One-time purchase", "Freemium", "Advertising", "Commission"]
                }
            ]
        }
    
    def _load_domain_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load domain-specific question templates."""
        
        return {
            "saas": [
                {
                    "text": "What integrations with other SaaS tools do your users need?",
                    "type": "text_long",
                    "priority": "medium"
                },
                {
                    "text": "Do you need multi-tenant architecture or single-tenant?",
                    "type": "single_choice",
                    "options": ["Multi-tenant", "Single-tenant", "Hybrid", "Not sure"],
                    "priority": "high"
                }
            ],
            "e_commerce": [
                {
                    "text": "What payment methods do you want to support?",
                    "type": "multiple_choice",
                    "options": ["Credit cards", "PayPal", "Stripe", "Bank transfers", "Cryptocurrency", "Buy now pay later"],
                    "priority": "high"
                },
                {
                    "text": "Do you need inventory management features?",
                    "type": "boolean",
                    "priority": "medium"
                }
            ],
            "mobile_app": [
                {
                    "text": "Which mobile platforms do you want to target?",
                    "type": "multiple_choice",
                    "options": ["iOS", "Android", "Cross-platform (React Native)", "Cross-platform (Flutter)", "Progressive Web App"],
                    "priority": "critical",
                    "required": True
                },
                {
                    "text": "Do you need offline functionality?",
                    "type": "boolean",
                    "priority": "medium"
                }
            ]
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None