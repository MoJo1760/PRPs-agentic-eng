name: "Flask PRP Generator - Entrepreneur Wrapper System"
description: |
  Comprehensive PRP for building a Flask-based wrapper system that transforms entrepreneurial ideas into production-ready PRPs using the PRPs-agentic-eng framework.

---

## Goal

**Feature Goal**: Create a Flask web application that serves as an intelligent wrapper around the PRPs-agentic-eng project, enabling entrepreneurs to input high-level business concepts and receive fully-formed, executable PRPs.

**Deliverable**: A production-ready Flask API with web interface that:
- Conducts intelligent questioning to extract requirements from entrepreneurs
- Performs automated research and context gathering
- Generates comprehensive PRPs using the existing PRP framework
- Executes validation loops and quality assessment

**Success Definition**: An entrepreneur can describe their idea in natural language, answer guided questions, and receive a complete PRP that an AI agent can execute successfully on the first pass.

## User Persona

**Target User**: Solo entrepreneurs, founders, and startup teams who have business ideas but lack deep technical implementation knowledge.

**Use Case**: An entrepreneur has a concept like "I want to build a SaaS platform for small restaurants to manage their inventory and orders" and needs a complete technical implementation roadmap.

**User Journey**:
1. User enters initial business concept via web form or API
2. System asks intelligent follow-up questions about business model, target users, key features
3. User answers questions through guided interface
4. System conducts automated research and generates comprehensive PRP
5. User receives complete PRP with implementation blueprint and validation commands

**Pain Points Addressed**:
- Bridge between business vision and technical implementation
- Eliminate guesswork in technical requirement gathering
- Reduce time from concept to implementable specification
- Provide validation frameworks for technical quality assurance

## Why

- **Market Need**: Entrepreneurs struggle to translate business ideas into technical specifications
- **Efficiency Gain**: Automated PRP generation vs. manual technical analysis (hours → minutes)
- **Quality Assurance**: Leverages proven PRP methodology for consistent, comprehensive outputs
- **Accessibility**: Makes AI-driven development accessible to non-technical founders
- **Scalability**: Enables rapid prototyping and validation of multiple business concepts

## What

### Core System Architecture

**Flask Web Application** with:
- RESTful API endpoints for idea submission and PRP generation
- Interactive web interface for guided questioning
- Integration with PRPs-agentic-eng project execution
- Research automation using web search and documentation analysis
- Quality scoring and validation pipeline

### User-Visible Features

- **Idea Intake Form**: Natural language business concept submission
- **Guided Questionnaire**: Dynamic, context-aware follow-up questions
- **Research Dashboard**: Real-time view of automated research progress
- **PRP Preview**: Generated PRP with quality metrics and completeness scoring
- **Execution Tracking**: Monitor PRP execution progress and validation results
- **Export Options**: Download PRPs in multiple formats (MD, JSON, PDF)

### Success Criteria

- [ ] Generate PRPs with 8+ quality score across all validation metrics
- [ ] Successfully execute 90%+ of generated PRPs through validation loops
- [ ] Complete end-to-end flow (concept → PRP → validation) in under 10 minutes
- [ ] Handle 20+ concurrent users with <2s response times
- [ ] Support 15+ different business domain types (SaaS, e-commerce, mobile apps, etc.)

## All Needed Context

### Context Completeness Check

_This PRP contains comprehensive context for implementing a Flask wrapper system that integrates with PRPs-agentic-eng, including API architecture, questionnaire logic, PRP generation workflows, and validation frameworks._

### Documentation & References

```yaml
# MUST READ - Flask and API Development Patterns
- url: https://flask.palletsprojects.com/en/3.0.x/patterns/
  why: Application factory pattern, configuration management, database integration
  critical: Proper Flask app structure prevents scaling issues and security vulnerabilities

- url: https://flask-restx.readthedocs.io/en/latest/
  why: API documentation, request validation, response serialization patterns
  critical: Proper API documentation and validation for production readiness

- file: /home/moj0/src/PRPs-agentic-eng/PRPs/templates/prp_base.md
  why: Complete PRP template structure and validation requirements
  pattern: Understand all sections, validation levels, and anti-patterns
  gotcha: PRPs must be self-contained with executable validation commands

- file: /home/moj0/src/PRPs-agentic-eng/PRPs/scripts/prp_runner.py
  why: Integration pattern for executing PRPs programmatically
  pattern: Command-line interface, output formatting, error handling
  gotcha: Requires specific tool permissions and environment setup

- docfile: PRPs/ai_docs/cc_commands.md
  why: Claude Code command patterns for PRP execution
  section: Tool permissions and execution workflow

# Business Domain Research
- url: https://medium.com/@sronmiz/collect-data-for-your-ds-research-by-creating-questionnaire-form-using-flask-and-sqlite-fe94e982c959
  why: Flask questionnaire patterns with data validation and storage
  critical: Form validation and progressive disclosure techniques for user experience

- url: https://github.com/vlevit/q10r
  why: JSON-based questionnaire generation and result storage patterns
  pattern: Dynamic form generation from configuration files
```

### Current Codebase Tree

```bash
PRPs-agentic-eng/
├── CLAUDE.md                          # Project instructions and methodology
├── PRPs/
│   ├── templates/                     # PRP templates (prp_base.md, etc.)
│   ├── scripts/prp_runner.py         # PRP execution engine
│   ├── ai_docs/                      # Claude Code documentation
│   └── *.md                          # Example PRPs
├── pyproject.toml                     # Python package config
├── src/                              # Source code directory
└── uv.lock                           # Dependency lock file
```

### Desired Codebase Tree with New Flask Wrapper

```bash
PRPs-agentic-eng/
├── flask_prp_wrapper/                # New Flask application
│   ├── app.py                        # Flask application factory
│   ├── models/                       # Data models and schemas
│   │   ├── __init__.py
│   │   ├── business_concept.py       # Business idea data model
│   │   ├── questionnaire.py          # Dynamic questionnaire model
│   │   └── prp_generation.py         # PRP generation data model
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   ├── questioning_engine.py     # Intelligent questioning logic
│   │   ├── research_service.py       # Automated research and context gathering
│   │   ├── prp_generator.py          # PRP generation using templates
│   │   └── validation_service.py     # PRP quality validation
│   ├── api/                          # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py                 # Main API routes
│   │   ├── business_concepts.py      # Business concept endpoints
│   │   └── prp_generation.py         # PRP generation endpoints
│   ├── templates/                    # Jinja2 web templates
│   │   ├── base.html
│   │   ├── index.html               # Landing page
│   │   ├── questionnaire.html       # Guided questionnaire interface
│   │   └── prp_preview.html         # PRP preview and download
│   ├── static/                      # Static assets
│   │   ├── css/style.css
│   │   └── js/questionnaire.js      # Dynamic questionnaire logic
│   ├── config.py                    # Flask configuration
│   ├── database.py                  # Database initialization
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       ├── prp_integration.py       # Integration with existing PRP system
│       └── quality_metrics.py       # PRP quality assessment
├── tests/                           # Test suite
│   ├── test_questioning_engine.py
│   ├── test_prp_generator.py
│   └── test_api_endpoints.py
└── requirements.txt                 # Python dependencies
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: PRPs-agentic-eng integration
# The existing prp_runner.py expects specific directory structure and file naming
# Must maintain compatibility with existing Claude Code tool permissions

# Flask-specific considerations
# Use application factory pattern to avoid circular imports
# Implement proper error handling for long-running PRP generation tasks
# Consider async task queue (Celery/Redis) for PRP generation process

# PRP Template Requirements
# Generated PRPs must include ALL required sections from prp_base.md template
# Validation commands must be executable in target environment
# Context sections must be comprehensive enough for AI agent success

# Web Interface Considerations
# Progressive questioning requires session management
# Large PRPs need streaming or chunked delivery to browser
# Research phase can take 2-5 minutes - need progress indicators

# Research Quality Constraints
# CRITICAL: Research service MUST prioritize official vendor documentation sources
# Priority order: Official docs > GitHub official repos > Stack Overflow > Blog posts
# Examples: docs.python.org, flask.palletsprojects.com, docs.aws.amazon.com
# This ensures higher quality, accurate, and up-to-date technical information
```

## Implementation Blueprint

### Data Models and Structure

Core data models ensuring type safety and validation consistency:

```python
# Pydantic models for request/response validation
class BusinessConceptRequest(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20, max_length=2000)
    target_users: Optional[str] = None
    business_model: Optional[str] = None
    domain: Optional[str] = None
    
class QuestionnaireResponse(BaseModel):
    question_id: str
    answer: str
    confidence_score: Optional[float] = None
    
class PRPGenerationRequest(BaseModel):
    concept_id: str
    questionnaire_responses: List[QuestionnaireResponse]
    research_depth: Literal["basic", "comprehensive", "deep"] = "comprehensive"
    
class GeneratedPRP(BaseModel):
    id: str
    title: str
    content: str
    quality_metrics: Dict[str, float]
    validation_commands: List[str]
    estimated_complexity: Literal["simple", "moderate", "complex"]
```

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: CREATE flask_prp_wrapper/config.py and app.py
  - IMPLEMENT: Flask application factory with proper configuration management
  - FOLLOW pattern: Flask application factory pattern with environment-based config
  - NAMING: FlaskPRPConfig class, create_app() factory function
  - PLACEMENT: Root of flask_prp_wrapper module

Task 2: CREATE flask_prp_wrapper/models/ data models
  - IMPLEMENT: Pydantic models for all data structures (BusinessConceptRequest, QuestionnaireResponse, etc.)
  - FOLLOW pattern: Pydantic BaseModel with proper validation and typing
  - NAMING: CamelCase for model classes, snake_case for fields
  - DEPENDENCIES: Pydantic v2 with Field validators
  - PLACEMENT: Separate model files by domain (business_concept.py, questionnaire.py, prp_generation.py)

Task 3: CREATE flask_prp_wrapper/services/questioning_engine.py
  - IMPLEMENT: Intelligent questioning service that generates dynamic follow-up questions
  - FOLLOW pattern: Service layer with async methods and dependency injection
  - NAMING: QuestioningEngine class with generate_questions(), analyze_responses() methods
  - DEPENDENCIES: Use OpenAI/Anthropic API for intelligent question generation
  - PLACEMENT: Core service in services/ directory

Task 4: CREATE flask_prp_wrapper/services/research_service.py
  - IMPLEMENT: Automated research service using web search and documentation analysis
  - FOLLOW pattern: Async service with retry logic and caching
  - NAMING: ResearchService class with gather_context(), analyze_domain() methods
  - DEPENDENCIES: Web search API, document parsing libraries
  - CONSTRAINT: PREFER official vendor documentation sources (docs.python.org, flask.palletsprojects.com, etc.) over third-party content
  - PLACEMENT: Service layer for research automation

Task 5: CREATE flask_prp_wrapper/services/prp_generator.py
  - IMPLEMENT: PRP generation service that creates PRPs using templates and research
  - FOLLOW pattern: Template engine with context injection and validation
  - NAMING: PRPGenerator class with generate_prp(), validate_prp() methods
  - DEPENDENCIES: Import PRP templates, integrate with prp_runner.py
  - PLACEMENT: Core PRP generation logic

Task 6: CREATE flask_prp_wrapper/api/routes.py
  - IMPLEMENT: Main API routes for business concept submission and PRP generation
  - FOLLOW pattern: Flask-RESTX with proper request/response validation
  - NAMING: RESTful endpoint naming (/api/v1/concepts, /api/v1/generate-prp)
  - DEPENDENCIES: Import all service classes and models
  - PLACEMENT: API layer with route organization

Task 7: CREATE flask_prp_wrapper/templates/ web interface
  - IMPLEMENT: Progressive web interface for guided questionnaire and PRP preview
  - FOLLOW pattern: Jinja2 templates with Bootstrap CSS and progressive enhancement
  - NAMING: Semantic HTML with clear component naming
  - DEPENDENCIES: Bootstrap 5, JavaScript for dynamic questionnaire
  - PLACEMENT: Templates directory with base template and feature-specific pages

Task 8: CREATE flask_prp_wrapper/utils/prp_integration.py
  - IMPLEMENT: Integration utilities for existing PRPs-agentic-eng system
  - FOLLOW pattern: Wrapper functions for prp_runner.py with proper error handling
  - NAMING: execute_prp(), validate_prp_output() utility functions
  - DEPENDENCIES: Subprocess management for prp_runner.py execution
  - PLACEMENT: Utility layer for system integration

Task 9: CREATE comprehensive test suite
  - IMPLEMENT: Unit tests for all services, integration tests for API endpoints
  - FOLLOW pattern: pytest with fixtures and mock external dependencies
  - NAMING: test_{component}_{scenario} function naming
  - COVERAGE: All service methods, API endpoints, and error conditions
  - PLACEMENT: tests/ directory with test organization matching source structure

Task 10: CREATE deployment configuration
  - IMPLEMENT: Docker configuration, requirements.txt, and deployment scripts
  - FOLLOW pattern: Production-ready deployment with proper security
  - NAMING: Standard deployment file naming (Dockerfile, docker-compose.yml)
  - DEPENDENCIES: Production WSGI server (gunicorn), proper environment management
  - PLACEMENT: Root directory deployment files
```

### Implementation Patterns & Key Details

```python
# Flask Application Factory Pattern
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    api.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    return app

# Intelligent Questioning Engine Pattern
class QuestioningEngine:
    async def generate_follow_up_questions(
        self, 
        concept: BusinessConceptRequest,
        previous_responses: List[QuestionnaireResponse]
    ) -> List[Question]:
        # PATTERN: Use AI to generate contextual questions
        # CRITICAL: Maintain question history to avoid repetition
        # GOTCHA: Limit to 10-15 questions max to prevent user fatigue
        
        context = self._build_question_context(concept, previous_responses)
        questions = await self._ai_client.generate_questions(context)
        return self._filter_and_prioritize_questions(questions)

# PRP Generation with Template Integration Pattern
class PRPGenerator:
    def __init__(self, prp_template_path: str):
        self.template = self._load_prp_template(prp_template_path)
        
    async def generate_prp(
        self, 
        concept: BusinessConceptRequest,
        research_context: ResearchContext
    ) -> GeneratedPRP:
        # PATTERN: Template substitution with validation
        # CRITICAL: Ensure all template sections are populated
        # GOTCHA: Validation commands must be executable in target environment
        
        prp_content = self._populate_template(concept, research_context)
        quality_score = self._assess_prp_quality(prp_content)
        
        if quality_score < 8.0:
            prp_content = await self._enhance_prp_content(prp_content)
            
        return GeneratedPRP(
            content=prp_content,
            quality_metrics=quality_score,
            validation_commands=self._extract_validation_commands(prp_content)
        )

# Research Service with Web Integration Pattern
class ResearchService:
    async def gather_business_domain_context(
        self, 
        domain: str,
        business_model: str
    ) -> ResearchContext:
        # PATTERN: Parallel research with caching
        # CRITICAL: PREFER official vendor documentation sources over third-party content
        # Priority order: Official docs > GitHub repos > Stack Overflow > Blog posts
        tasks = [
            self._research_competitors(domain),
            self._research_technical_patterns(business_model),
            self._research_validation_approaches(domain)
        ]
        
        results = await asyncio.gather(*tasks)
        return ResearchContext.from_research_results(results)
    
    def _prioritize_documentation_sources(self, search_results: List[SearchResult]) -> List[SearchResult]:
        # CONSTRAINT: Prefer official vendor documentation
        # Official domains get highest priority: docs.python.org, flask.palletsprojects.com, etc.
        official_domains = [
            'docs.python.org', 'flask.palletsprojects.com', 'pydantic-docs.helpmanual.io',
            'docs.aws.amazon.com', 'cloud.google.com', 'docs.microsoft.com',
            'kubernetes.io', 'docker.com', 'github.com' # GitHub for official repos
        ]
        
        # Sort results: official docs first, then by relevance score
        return sorted(search_results, key=lambda x: (
            x.domain not in official_domains,  # False (0) for official, True (1) for others
            -x.relevance_score  # Higher relevance first within same category
        ))
```

### Integration Points

```yaml
DATABASE:
  - choice: SQLite for development, PostgreSQL for production
  - migrations: Flask-Migrate for database schema management
  - models: SQLAlchemy ORM with relationship mapping

EXTERNAL_APIS:
  - web_search: Integrate with search APIs for domain research
  - ai_services: OpenAI/Anthropic for intelligent questioning and PRP enhancement
  - rate_limiting: Implement proper rate limiting and retry logic

PRP_SYSTEM_INTEGRATION:
  - execution: Subprocess calls to existing prp_runner.py
  - file_management: Proper PRP file creation and organization
  - validation: Integration with existing validation commands

FRONTEND:
  - framework: Progressive enhancement with vanilla JavaScript
  - styling: Bootstrap 5 for responsive design
  - real_time: WebSocket or Server-Sent Events for progress updates
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
ruff check flask_prp_wrapper/ --fix     # Auto-format and fix linting issues
mypy flask_prp_wrapper/                 # Type checking
ruff format flask_prp_wrapper/          # Ensure consistent formatting

# Dependency validation
uv sync                                 # Ensure all dependencies are installed
pip-audit                              # Security audit of dependencies

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test each component as it's created
uv run pytest tests/test_questioning_engine.py -v
uv run pytest tests/test_research_service.py -v  
uv run pytest tests/test_prp_generator.py -v
uv run pytest tests/test_api_endpoints.py -v

# Full test suite with coverage
uv run pytest tests/ --cov=flask_prp_wrapper --cov-report=term-missing -v

# Performance tests for long-running operations
uv run pytest tests/test_performance.py -v --timeout=30

# Expected: All tests pass with >85% coverage. Debug and fix any failures.
```

### Level 3: Integration Testing (System Validation)

```bash
# Flask application startup validation
export FLASK_ENV=development
export FLASK_APP=flask_prp_wrapper.app:create_app
uv run flask run --port 5000 &
sleep 5  # Allow startup time

# Health check validation
curl -f http://localhost:5000/health || echo "Health check failed"

# API endpoint testing
curl -X POST http://localhost:5000/api/v1/concepts \
  -H "Content-Type: application/json" \
  -d '{"title": "Test SaaS Platform", "description": "A platform for managing small business inventory and orders", "domain": "saas"}' \
  | jq .

# Questionnaire generation testing
curl -X POST http://localhost:5000/api/v1/generate-questions \
  -H "Content-Type: application/json" \
  -d '{"concept_id": "test-concept-123"}' \
  | jq .

# PRP generation end-to-end test
curl -X POST http://localhost:5000/api/v1/generate-prp \
  -H "Content-Type: application/json" \
  -d '{"concept_id": "test-concept-123", "questionnaire_responses": [{"question_id": "q1", "answer": "Restaurant management"}]}' \
  | jq .

# Web interface validation
curl -f http://localhost:5000/ || echo "Web interface failed"

# Clean up test processes
pkill -f "flask run"

# Expected: All endpoints respond correctly, PRP generation completes, web interface loads
```

### Level 4: Creative & Domain-Specific Validation

```bash
# PRP Quality Validation
# Generate sample PRPs and validate through existing PRP runner
uv run python -c "
from flask_prp_wrapper.services.prp_generator import PRPGenerator
from flask_prp_wrapper.models.business_concept import BusinessConceptRequest

# Test PRP generation with sample business concept
concept = BusinessConceptRequest(
    title='AI-Powered Recipe Recommendation System',
    description='A mobile app that uses AI to recommend recipes based on dietary preferences, available ingredients, and cooking skill level',
    domain='mobile_app',
    business_model='freemium'
)

generator = PRPGenerator()
prp = await generator.generate_prp(concept, research_context)
print(f'Generated PRP quality score: {prp.quality_metrics}')
"

# Execute generated PRP through existing system
cp /tmp/generated_test_prp.md PRPs/test-generated-prp.md
uv run PRPs/scripts/prp_runner.py --prp test-generated-prp --output-format json | jq .

# Business Domain Coverage Testing
# Test different business domains to ensure comprehensive coverage
domains=("saas" "e_commerce" "mobile_app" "marketplace" "fintech" "healthcare")
for domain in "${domains[@]}"; do
  echo "Testing domain: $domain"
  curl -X POST http://localhost:5000/api/v1/test-domain-coverage \
    -H "Content-Type: application/json" \
    -d "{\"domain\": \"$domain\"}" | jq .success
done

# Load Testing for Concurrent Users
# Simulate 20 concurrent users generating PRPs
uv run locust -f tests/load_test.py --host=http://localhost:5000 --users=20 --spawn-rate=2 --run-time=60s --headless

# Questionnaire Logic Validation
# Test dynamic questioning with various business scenarios
uv run python tests/validate_questionnaire_logic.py

# Expected: PRPs score 8+, domain coverage 95%+, load test passes, questionnaire logic handles edge cases
```

## Final Validation Checklist

### Technical Validation

- [ ] All 4 validation levels completed successfully
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check flask_prp_wrapper/`
- [ ] No type errors: `uv run mypy flask_prp_wrapper/`
- [ ] No formatting issues: `uv run ruff format flask_prp_wrapper/ --check`
- [ ] Security audit passes: `pip-audit`

### Feature Validation

- [ ] End-to-end flow: concept submission → questioning → PRP generation → validation
- [ ] Generated PRPs achieve 8+ quality score across all metrics
- [ ] 15+ business domains supported with appropriate questionnaire logic
- [ ] Web interface responsive and accessible on mobile/desktop
- [ ] API documentation complete and accurate
- [ ] Integration with existing PRPs-agentic-eng system successful

### Code Quality Validation

- [ ] Flask application factory pattern implemented correctly
- [ ] Service layer separation with proper dependency injection
- [ ] Database models and migrations working correctly
- [ ] Error handling comprehensive with proper logging
- [ ] Configuration management for development/production environments
- [ ] Security best practices followed (input validation, SQL injection prevention, etc.)

### Business Logic Validation

- [ ] Intelligent questioning generates relevant, non-repetitive questions
- [ ] Research automation gathers comprehensive context for PRP generation
- [ ] PRP quality assessment provides meaningful metrics
- [ ] Generated PRPs executable through existing validation commands
- [ ] System handles edge cases (incomplete responses, research failures, etc.)

### Deployment Validation

- [ ] Docker containerization working correctly
- [ ] Environment variables properly configured
- [ ] Production deployment scripts tested
- [ ] Database migrations work in production environment
- [ ] Monitoring and logging configured for production use

---

## Anti-Patterns to Avoid

- ❌ Don't generate PRPs without comprehensive research context - they will fail validation
- ❌ Don't skip questionnaire validation - incomplete requirements lead to poor PRPs
- ❌ Don't hardcode business domain logic - use configuration-driven approach
- ❌ Don't ignore PRP quality metrics - enforce minimum standards before output
- ❌ Don't block UI during long PRP generation - implement async task processing
- ❌ Don't trust user input without validation - sanitize and validate all inputs
- ❌ Don't create monolithic services - maintain clear separation of concerns
- ❌ Don't skip integration testing with existing PRP system - ensure compatibility