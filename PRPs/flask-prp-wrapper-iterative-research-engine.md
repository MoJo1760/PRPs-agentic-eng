name: "Flask PRP Wrapper - Iterative Research Engine"
description: |
  Comprehensive PRP for enhancing the Flask PRP wrapper with an iterative research engine that continues asking questions and performing research from official sources until there are no more open questions.

---

## Goal

**Feature Goal**: Enhance the existing Flask PRP wrapper with an intelligent iterative research engine that automatically identifies gaps in requirements, generates follow-up questions, conducts official source research, and continues this cycle until comprehensive coverage is achieved.

**Deliverable**: An enhanced Flask PRP wrapper service that includes:
- Iterative questioning engine that identifies knowledge gaps
- Official source research automation with quality validation
- Dynamic question generation based on research findings
- Comprehensive coverage validation with stopping criteria
- Research quality scoring and gap analysis

**Success Definition**: The system can take a basic business concept, automatically identify and fill knowledge gaps through iterative research and questioning, achieving 95%+ requirement completeness before PRP generation.

## User Persona

**Target User**: Entrepreneurs and founders who have incomplete business concepts and need comprehensive requirement analysis.

**Use Case**: A user submits "Build a food delivery app" and the system automatically identifies gaps (payment processing, driver management, restaurant onboarding, etc.), researches official documentation for each area, generates targeted questions, and continues until all aspects are thoroughly covered.

**User Journey**:
1. User submits basic business concept
2. System conducts initial research and identifies knowledge gaps
3. System generates targeted questions based on gaps and research
4. User answers questions, system analyzes responses for new gaps
5. System conducts additional research on newly identified areas
6. Process repeats until comprehensive coverage achieved
7. System generates complete PRP with all gaps filled

**Pain Points Addressed**:
- Eliminates incomplete requirement gathering
- Prevents overlooked technical considerations
- Reduces back-and-forth clarification cycles
- Ensures comprehensive technical coverage

## Why

- **Comprehensive Coverage**: Ensures no critical aspects are missed in requirement gathering
- **Quality Assurance**: Official source research provides accurate, up-to-date technical information
- **Efficiency**: Automated research reduces manual investigation time
- **Standardization**: Consistent research methodology across all domains
- **User Experience**: Users don't need to know what they don't know

## What

### Core Enhancement Architecture

**Iterative Research Engine** consisting of:
- Gap Analysis Service: Identifies missing information in current concept
- Official Source Research Service: Prioritizes vendor documentation and official sources
- Dynamic Question Generator: Creates targeted questions based on research findings
- Coverage Validator: Determines when sufficient information has been gathered
- Research Quality Assessor: Validates research quality and identifies weak areas

### User-Visible Features

- **Research Progress Dashboard**: Real-time view of research coverage across domains
- **Gap Analysis Report**: Visual representation of identified knowledge gaps
- **Question Confidence Scoring**: Shows how questions relate to identified gaps
- **Research Source Quality Indicators**: Displays official vs. third-party source ratios
- **Coverage Completion Metrics**: Progress toward comprehensive requirement coverage
- **Auto-Stop Criteria**: System automatically stops when coverage threshold met

### Success Criteria

- [ ] Achieve 95%+ requirement coverage before PRP generation
- [ ] Identify and research 90%+ of domain-specific technical considerations
- [ ] Generate follow-up questions with 85%+ relevance to identified gaps
- [ ] Prioritize official documentation sources (docs.*, official GitHub repos) >80% of the time
- [ ] Complete iterative research cycle in <15 minutes for complex domains
- [ ] Stop iteration when gap coverage threshold met without user intervention

## All Needed Context

### Context Completeness Check

_This PRP contains comprehensive context for implementing an iterative research engine that enhances the existing Flask PRP wrapper with gap analysis, official source research, and intelligent stopping criteria._

### Documentation & References

```yaml
# MUST READ - Current Flask PRP Wrapper Implementation
- file: /home/moj0/src/PRPs-agentic-eng/flask_prp_wrapper/services/research_service.py
  why: Current research service implementation with official docs prioritization
  pattern: ResearchService class structure, web search integration patterns, fallback methods
  gotcha: Already has official docs prioritization and caching - build on this foundation

- file: /home/moj0/src/PRPs-agentic-eng/flask_prp_wrapper/services/questioning_engine.py
  why: Current questioning engine with domain-specific templates
  pattern: QuestioningEngine class, question generation, session management
  gotcha: Has static question templates - need to make dynamic based on research gaps

- file: /home/moj0/src/PRPs-agentic-eng/flask_prp_wrapper/api/routes.py
  why: Current API endpoints and flow patterns
  pattern: Async route handling, session management, error handling
  gotcha: Current flow is linear - need to add iterative loop capability

# Research Quality and Official Sources
- url: https://flask.palletsprojects.com/patterns/
  why: Flask application patterns for service architecture
  critical: Proper service layer patterns for complex research workflows

- url: https://docs.python.org/3/library/asyncio.html
  why: Async/await patterns for concurrent research operations
  critical: Proper async context management for parallel research tasks

# Gap Analysis and Coverage Validation
- url: https://en.wikipedia.org/wiki/Requirement_analysis
  why: Understanding requirement completeness methodologies
  pattern: Coverage metrics, gap identification techniques

- file: /home/moj0/src/PRPs-agentic-eng/PRPs/templates/prp_base.md
  why: PRP template structure for understanding coverage requirements
  pattern: All required sections and validation levels
  gotcha: Generated PRPs must meet all template requirements - use for gap analysis
```

### Current Codebase Tree

```bash
PRPs-agentic-eng/
├── flask_prp_wrapper/
│   ├── app.py                        # Flask application factory
│   ├── config.py                     # Configuration management
│   ├── models/
│   │   ├── business_concept.py       # Business concept models
│   │   └── questionnaire.py          # Questionnaire models
│   ├── services/
│   │   ├── questioning_engine.py     # Current questioning service
│   │   ├── research_service.py       # Current research service (has official docs priority)
│   │   └── prp_generator.py          # PRP generation service
│   ├── api/
│   │   └── routes.py                 # Current API endpoints
│   └── utils/
│       └── prp_integration.py        # PRP system integration
├── PRPs/
│   ├── templates/prp_base.md         # PRP template for gap analysis
│   └── scripts/prp_runner.py         # PRP execution engine
└── pyproject.toml
```

### Enhanced Codebase Tree with Iterative Research Engine

```bash
PRPs-agentic-eng/
├── flask_prp_wrapper/
│   ├── services/
│   │   ├── gap_analysis_service.py          # NEW: Identifies knowledge gaps
│   │   ├── iterative_research_engine.py     # NEW: Orchestrates research iterations
│   │   ├── coverage_validator.py            # NEW: Validates requirement completeness
│   │   ├── research_quality_assessor.py     # NEW: Assesses research source quality
│   │   ├── questioning_engine.py            # ENHANCED: Dynamic question generation
│   │   └── research_service.py              # ENHANCED: Gap-driven research
│   ├── models/
│   │   ├── research_iteration.py            # NEW: Research iteration tracking
│   │   ├── gap_analysis.py                  # NEW: Gap analysis data models
│   │   └── coverage_metrics.py              # NEW: Coverage validation models
│   ├── api/
│   │   └── routes.py                        # ENHANCED: Iterative research endpoints
│   └── utils/
│       └── domain_knowledge_base.py         # NEW: Domain-specific knowledge templates
├── tests/
│   ├── test_iterative_research_engine.py   # NEW: Comprehensive engine testing
│   ├── test_gap_analysis_service.py        # NEW: Gap analysis testing
│   └── test_coverage_validator.py          # NEW: Coverage validation testing
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: Current research_service.py already has official docs prioritization
# Build on existing ResearchService rather than replacing it
# Priority order already implemented: Official docs > GitHub repos > Stack Overflow > Blog posts

# Flask async handling considerations
# Current routes.py uses asyncio.new_event_loop() pattern - maintain consistency
# Long-running research iterations need proper async handling and timeout management

# Gap Analysis Challenges
# Knowledge domains are vast - need domain-specific coverage templates
# Stopping criteria must balance completeness with practical time limits
# Research quality vs. quantity tradeoff in iteration decisions

# PRP Template Integration
# prp_base.md template defines required sections - use as coverage checklist
# Generated PRPs must pass all validation levels - research must support this

# Official Source Constraints
# CRITICAL: Continue prioritizing official vendor documentation
# Current domains list in research_service.py should be expanded
# Rate limiting considerations for multiple research API calls
# Cache invalidation for iterative research cycles
```

## Implementation Blueprint

### Data Models and Structure

Core data models for iterative research tracking and gap analysis:

```python
# Gap Analysis Models
class KnowledgeGap(BaseModel):
    id: str
    domain: str
    category: str
    description: str
    priority: Literal["critical", "high", "medium", "low"]
    identified_at: datetime
    research_attempts: int = 0
    filled: bool = False
    confidence_score: float = 0.0

class GapAnalysisResult(BaseModel):
    concept_id: str
    identified_gaps: List[KnowledgeGap]
    coverage_percentage: float
    domain_completeness: Dict[str, float]
    analysis_timestamp: datetime
    next_research_areas: List[str]

# Research Iteration Models
class ResearchIteration(BaseModel):
    id: str
    concept_id: str
    iteration_number: int
    gaps_targeted: List[str]
    research_results: List[SearchResult]
    questions_generated: List[Question]
    coverage_improvement: float
    official_source_ratio: float
    started_at: datetime
    completed_at: Optional[datetime] = None

# Coverage Validation Models
class CoverageMetrics(BaseModel):
    overall_coverage: float
    domain_coverage: Dict[str, float]
    technical_requirements_coverage: float
    business_model_coverage: float
    integration_coverage: float
    validation_coverage: float
    stopping_criteria_met: bool
    recommended_next_steps: List[str]
```

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: CREATE flask_prp_wrapper/models/gap_analysis.py and related models
  - IMPLEMENT: KnowledgeGap, GapAnalysisResult, ResearchIteration, CoverageMetrics models
  - FOLLOW pattern: Existing models in flask_prp_wrapper/models/ (Pydantic BaseModel structure)
  - NAMING: CamelCase for model classes, snake_case for fields
  - PLACEMENT: New model files in models/ directory
  - DEPENDENCIES: datetime, typing, Literal from existing models

Task 2: CREATE flask_prp_wrapper/services/gap_analysis_service.py
  - IMPLEMENT: GapAnalysisService class with domain-specific gap identification
  - FOLLOW pattern: services/research_service.py (async service structure, caching patterns)
  - NAMING: GapAnalysisService class with analyze_concept_gaps(), identify_missing_areas() methods
  - DEPENDENCIES: Import new gap analysis models, reference prp_base.md template structure
  - PLACEMENT: Core service in services/ directory

Task 3: CREATE flask_prp_wrapper/services/coverage_validator.py
  - IMPLEMENT: CoverageValidator class with stopping criteria and completeness assessment
  - FOLLOW pattern: services/questioning_engine.py (analysis and scoring patterns)
  - NAMING: CoverageValidator class with validate_coverage(), assess_completeness() methods
  - DEPENDENCIES: Import coverage metrics models, reference PRP template requirements
  - PLACEMENT: Validation service in services/ directory

Task 4: CREATE flask_prp_wrapper/services/research_quality_assessor.py
  - IMPLEMENT: ResearchQualityAssessor class for evaluating research source quality
  - FOLLOW pattern: services/research_service.py (_calculate_research_quality_score method)
  - NAMING: ResearchQualityAssessor class with assess_source_quality(), validate_official_ratio() methods
  - DEPENDENCIES: Extend existing research quality patterns from research_service.py
  - PLACEMENT: Quality assessment service in services/ directory

Task 5: CREATE flask_prp_wrapper/services/iterative_research_engine.py
  - IMPLEMENT: IterativeResearchEngine class orchestrating the complete research cycle
  - FOLLOW pattern: services/prp_generator.py (complex workflow orchestration)
  - NAMING: IterativeResearchEngine class with conduct_iterative_research(), orchestrate_cycle() methods
  - DEPENDENCIES: Import all services created in Tasks 2-4, plus existing questioning and research services
  - PLACEMENT: Main orchestration service in services/ directory

Task 6: ENHANCE flask_prp_wrapper/services/questioning_engine.py
  - MODIFY: Add gap-driven question generation methods
  - IMPLEMENT: generate_gap_targeted_questions(), analyze_response_for_new_gaps() methods
  - FOLLOW pattern: Existing QuestioningEngine class structure and patterns
  - PRESERVE: All existing functionality while adding gap-analysis capabilities
  - DEPENDENCIES: Import gap analysis models from Task 1

Task 7: ENHANCE flask_prp_wrapper/services/research_service.py
  - MODIFY: Add gap-targeted research methods and iteration support
  - IMPLEMENT: research_specific_gaps(), conduct_targeted_research() methods
  - FOLLOW pattern: Existing ResearchService patterns and official docs prioritization
  - PRESERVE: Existing gather_business_domain_context() and official source prioritization
  - DEPENDENCIES: Import gap analysis models, maintain existing functionality

Task 8: ENHANCE flask_prp_wrapper/api/routes.py
  - MODIFY: Add iterative research endpoints and enhance existing flow
  - IMPLEMENT: /concepts/{id}/iterative-research, /research-iterations/{id}/status endpoints
  - FOLLOW pattern: Existing route structure, async handling, error management
  - PRESERVE: All existing endpoints while adding iterative research capability
  - DEPENDENCIES: Import iterative research engine and new models

Task 9: CREATE flask_prp_wrapper/utils/domain_knowledge_base.py
  - IMPLEMENT: Domain-specific knowledge templates and coverage requirements
  - FOLLOW pattern: utils/prp_integration.py (utility functions and integration helpers)
  - NAMING: DomainKnowledgeBase class with get_domain_requirements(), get_coverage_template() methods
  - DEPENDENCIES: Reference PRP template structure and domain-specific requirements
  - PLACEMENT: Utility for domain knowledge management

Task 10: CREATE comprehensive test suite for all new components
  - IMPLEMENT: Unit tests for all new services and enhanced functionality
  - FOLLOW pattern: Existing test patterns in tests/ directory
  - NAMING: test_{service}_{scenario} function naming
  - COVERAGE: Gap analysis, research iteration, coverage validation, quality assessment
  - PLACEMENT: tests/ directory with comprehensive coverage
```

### Implementation Patterns & Key Details

```python
# Gap Analysis Service Pattern
class GapAnalysisService:
    def __init__(self, domain_knowledge_base: DomainKnowledgeBase):
        self.domain_kb = domain_knowledge_base
        self._gap_cache: Dict[str, List[KnowledgeGap]] = {}
        
    async def analyze_concept_gaps(
        self, 
        concept: BusinessConceptRequest,
        existing_research: ResearchContext
    ) -> GapAnalysisResult:
        # PATTERN: Domain-driven gap identification
        # CRITICAL: Use PRP template as coverage checklist
        domain_requirements = self.domain_kb.get_domain_requirements(concept.domain)
        
        identified_gaps = []
        for requirement in domain_requirements:
            if not self._is_requirement_covered(requirement, existing_research):
                gap = KnowledgeGap(
                    id=f"gap_{requirement.category}_{len(identified_gaps)}",
                    domain=concept.domain,
                    category=requirement.category,
                    description=requirement.description,
                    priority=requirement.priority
                )
                identified_gaps.append(gap)
        
        coverage_percentage = self._calculate_coverage_percentage(
            domain_requirements, identified_gaps
        )
        
        return GapAnalysisResult(
            concept_id=concept.id,
            identified_gaps=identified_gaps,
            coverage_percentage=coverage_percentage,
            domain_completeness=self._analyze_domain_completeness(identified_gaps),
            analysis_timestamp=datetime.utcnow(),
            next_research_areas=self._prioritize_research_areas(identified_gaps)
        )

# Iterative Research Engine Pattern
class IterativeResearchEngine:
    def __init__(
        self,
        gap_analyzer: GapAnalysisService,
        research_service: ResearchService,
        questioning_engine: QuestioningEngine,
        coverage_validator: CoverageValidator,
        max_iterations: int = 5
    ):
        self.gap_analyzer = gap_analyzer
        self.research_service = research_service
        self.questioning_engine = questioning_engine
        self.coverage_validator = coverage_validator
        self.max_iterations = max_iterations
        
    async def conduct_iterative_research(
        self,
        concept: BusinessConceptRequest,
        initial_responses: List[QuestionnaireResponse] = None
    ) -> IterativeResearchResult:
        # PATTERN: Iterative research with stopping criteria
        # CRITICAL: Maintain official source prioritization throughout iterations
        
        iterations = []
        current_research_context = None
        
        for iteration_num in range(self.max_iterations):
            # Gap Analysis Phase
            gap_analysis = await self.gap_analyzer.analyze_concept_gaps(
                concept, current_research_context
            )
            
            # Coverage Check - Stop if sufficient
            coverage_metrics = await self.coverage_validator.validate_coverage(
                gap_analysis
            )
            
            if coverage_metrics.stopping_criteria_met:
                logger.info(f"Stopping criteria met at iteration {iteration_num}")
                break
            
            # Research Phase - Target specific gaps
            research_results = await self.research_service.research_specific_gaps(
                gap_analysis.next_research_areas
            )
            
            # Question Generation Phase - Based on new research
            new_questions = await self.questioning_engine.generate_gap_targeted_questions(
                gap_analysis.identified_gaps, research_results
            )
            
            # Create iteration record
            iteration = ResearchIteration(
                id=f"iter_{concept.id}_{iteration_num}",
                concept_id=concept.id,
                iteration_number=iteration_num,
                gaps_targeted=gap_analysis.next_research_areas,
                research_results=research_results,
                questions_generated=new_questions,
                coverage_improvement=self._calculate_coverage_improvement(gap_analysis),
                official_source_ratio=self._calculate_official_source_ratio(research_results),
                started_at=datetime.utcnow()
            )
            
            iterations.append(iteration)
            
            # Update research context for next iteration
            current_research_context = self._merge_research_contexts(
                current_research_context, research_results
            )
        
        return IterativeResearchResult(
            concept_id=concept.id,
            iterations=iterations,
            final_coverage_metrics=coverage_metrics,
            total_gaps_identified=len(gap_analysis.identified_gaps),
            gaps_filled=len([g for g in gap_analysis.identified_gaps if g.filled]),
            final_research_context=current_research_context
        )

# Coverage Validator Pattern
class CoverageValidator:
    def __init__(self, minimum_coverage_threshold: float = 0.95):
        self.min_coverage = minimum_coverage_threshold
        
    async def validate_coverage(self, gap_analysis: GapAnalysisResult) -> CoverageMetrics:
        # PATTERN: Multi-dimensional coverage assessment
        # CONSTRAINT: Use PRP template requirements as coverage baseline
        
        overall_coverage = gap_analysis.coverage_percentage
        domain_coverage = gap_analysis.domain_completeness
        
        # Calculate specific coverage areas
        technical_coverage = self._assess_technical_requirements_coverage(gap_analysis)
        business_coverage = self._assess_business_model_coverage(gap_analysis)
        integration_coverage = self._assess_integration_coverage(gap_analysis)
        validation_coverage = self._assess_validation_coverage(gap_analysis)
        
        # Determine if stopping criteria met
        stopping_criteria_met = (
            overall_coverage >= self.min_coverage and
            all(coverage >= 0.85 for coverage in domain_coverage.values()) and
            technical_coverage >= 0.90 and
            validation_coverage >= 0.80
        )
        
        return CoverageMetrics(
            overall_coverage=overall_coverage,
            domain_coverage=domain_coverage,
            technical_requirements_coverage=technical_coverage,
            business_model_coverage=business_coverage,
            integration_coverage=integration_coverage,
            validation_coverage=validation_coverage,
            stopping_criteria_met=stopping_criteria_met,
            recommended_next_steps=self._generate_next_steps(gap_analysis, stopping_criteria_met)
        )
```

### Integration Points

```yaml
ENHANCED_RESEARCH_SERVICE:
  - extend: ResearchService.gather_business_domain_context()
  - add: research_specific_gaps(), conduct_targeted_research()
  - preserve: Official documentation prioritization patterns
  - enhance: Gap-driven research queries and result filtering

ENHANCED_QUESTIONING_ENGINE:
  - extend: QuestioningEngine.generate_questions()
  - add: generate_gap_targeted_questions(), analyze_response_for_new_gaps()
  - preserve: Existing domain templates and session management
  - enhance: Dynamic question generation based on research findings

API_ENDPOINTS:
  - add: POST /api/v1/concepts/{id}/iterative-research
  - add: GET /api/v1/research-iterations/{id}/status
  - add: GET /api/v1/concepts/{id}/coverage-metrics
  - enhance: Existing endpoints with iterative research status

WORKFLOW_INTEGRATION:
  - modify: Concept submission flow to include iterative research option
  - add: Research iteration tracking and progress monitoring
  - enhance: PRP generation with comprehensive research context
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
ruff check flask_prp_wrapper/services/gap_analysis_service.py --fix
ruff check flask_prp_wrapper/services/iterative_research_engine.py --fix
ruff check flask_prp_wrapper/services/coverage_validator.py --fix
ruff check flask_prp_wrapper/models/gap_analysis.py --fix

# Type checking for new components
mypy flask_prp_wrapper/services/gap_analysis_service.py
mypy flask_prp_wrapper/services/iterative_research_engine.py
mypy flask_prp_wrapper/models/gap_analysis.py

# Project-wide validation
ruff check flask_prp_wrapper/ --fix
mypy flask_prp_wrapper/
ruff format flask_prp_wrapper/

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test new services individually
uv run pytest tests/test_gap_analysis_service.py -v
uv run pytest tests/test_iterative_research_engine.py -v
uv run pytest tests/test_coverage_validator.py -v
uv run pytest tests/test_research_quality_assessor.py -v

# Test enhanced existing services
uv run pytest tests/test_questioning_engine.py -v  # Test new gap-driven methods
uv run pytest tests/test_research_service.py -v    # Test enhanced research methods

# Full service test suite
uv run pytest tests/ --cov=flask_prp_wrapper.services --cov-report=term-missing -v

# Expected: All tests pass with >85% coverage. Debug and fix any failures.
```

### Level 3: Integration Testing (System Validation)

```bash
# Flask application startup validation
export FLASK_ENV=testing
export FLASK_APP=flask_prp_wrapper.app:create_app
uv run flask run --port 5000 &
sleep 5

# Health check validation
curl -f http://localhost:5000/health || echo "Health check failed"

# Iterative research flow testing
concept_id=$(curl -X POST http://localhost:5000/api/v1/concepts \
  -H "Content-Type: application/json" \
  -d '{"title": "Food Delivery Platform", "description": "A comprehensive food delivery platform connecting restaurants, drivers, and customers", "domain": "marketplace", "business_model": "commission"}' \
  | jq -r '.concept_id')

echo "Created concept: $concept_id"

# Start iterative research
research_id=$(curl -X POST http://localhost:5000/api/v1/concepts/$concept_id/iterative-research \
  -H "Content-Type: application/json" \
  -d '{"max_iterations": 3, "coverage_threshold": 0.95}' \
  | jq -r '.research_id')

echo "Started iterative research: $research_id"

# Monitor research progress
for i in {1..10}; do
  status=$(curl -s http://localhost:5000/api/v1/research-iterations/$research_id/status | jq -r '.status')
  echo "Research iteration $i status: $status"
  
  if [ "$status" = "completed" ]; then
    break
  fi
  
  sleep 3
done

# Validate final coverage metrics
curl -s http://localhost:5000/api/v1/concepts/$concept_id/coverage-metrics | jq .

# Generate PRP with comprehensive research
curl -X POST http://localhost:5000/api/v1/concepts/$concept_id/generate-prp \
  -H "Content-Type: application/json" | jq .

# Clean up
pkill -f "flask run"

# Expected: Research completes with high coverage, PRP generation succeeds
```

### Level 4: Creative & Domain-Specific Validation

```bash
# Gap Analysis Quality Validation
uv run python -c "
from flask_prp_wrapper.services.gap_analysis_service import GapAnalysisService
from flask_prp_wrapper.models.business_concept import BusinessConceptRequest
from flask_prp_wrapper.utils.domain_knowledge_base import DomainKnowledgeBase

# Test gap analysis with minimal concept
minimal_concept = BusinessConceptRequest(
    title='Simple Food App',
    description='An app for ordering food',
    domain='mobile_app'
)

kb = DomainKnowledgeBase()
gap_service = GapAnalysisService(kb)
gaps = await gap_service.analyze_concept_gaps(minimal_concept, None)
print(f'Identified {len(gaps.identified_gaps)} gaps for minimal concept')
print(f'Coverage: {gaps.coverage_percentage:.1f}%')
"

# Research Quality Official Source Validation
uv run python -c "
from flask_prp_wrapper.services.research_quality_assessor import ResearchQualityAssessor
from flask_prp_wrapper.services.research_service import SearchResult

# Test official source prioritization
results = [
    SearchResult(title='Official Python Docs', url='https://docs.python.org/', 
                snippet='Official documentation', domain='docs.python.org', 
                relevance_score=9.0, is_official_docs=True),
    SearchResult(title='Stack Overflow', url='https://stackoverflow.com/', 
                snippet='Community answer', domain='stackoverflow.com', 
                relevance_score=8.0, is_official_docs=False)
]

assessor = ResearchQualityAssessor()
quality = assessor.assess_source_quality(results)
print(f'Official source ratio: {quality.official_source_ratio:.2f}')
print(f'Research quality score: {quality.overall_quality_score:.1f}')
"

# Coverage Validation Testing
# Test different business domains for comprehensive coverage
domains=("saas" "e_commerce" "mobile_app" "marketplace" "fintech" "healthcare")
for domain in "${domains[@]}"; do
  echo "Testing iterative research coverage for domain: $domain"
  
  coverage=$(curl -s -X POST http://localhost:5000/api/v1/test-coverage-analysis \
    -H "Content-Type: application/json" \
    -d "{\"domain\": \"$domain\", \"description\": \"Complex $domain application with multiple integrations\"}" \
    | jq -r '.final_coverage_percentage')
  
  echo "Final coverage for $domain: $coverage%"
  
  if (( $(echo "$coverage < 95" | bc -l) )); then
    echo "WARNING: Coverage below threshold for $domain"
  fi
done

# Iterative Research Performance Testing
# Test research engine with complex, gap-rich concepts
uv run python tests/performance/test_iterative_research_performance.py

# Research Source Quality Validation
# Verify official source prioritization in real research queries
uv run python tests/validation/validate_official_source_research.py

# Expected: All domains achieve >95% coverage, official source ratio >80%, performance <15min
```

## Final Validation Checklist

### Technical Validation

- [ ] All 4 validation levels completed successfully
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check flask_prp_wrapper/`
- [ ] No type errors: `uv run mypy flask_prp_wrapper/`
- [ ] No formatting issues: `uv run ruff format flask_prp_wrapper/ --check`

### Feature Validation

- [ ] Iterative research achieves 95%+ coverage for complex business concepts
- [ ] Gap analysis identifies domain-specific technical requirements
- [ ] Official source research maintains >80% official documentation ratio
- [ ] Coverage validator properly determines stopping criteria
- [ ] Research iterations complete within 15-minute time limit
- [ ] Enhanced questioning engine generates relevant gap-targeted questions

### Integration Validation

- [ ] Enhanced services maintain backward compatibility with existing functionality
- [ ] API endpoints support both traditional and iterative research workflows
- [ ] Research quality assessment properly evaluates source credibility
- [ ] Coverage metrics accurately reflect requirement completeness
- [ ] PRP generation incorporates comprehensive iterative research results

### Business Logic Validation

- [ ] System automatically identifies knowledge gaps in business concepts
- [ ] Iterative research stops when coverage threshold met
- [ ] Question generation targets identified gaps effectively
- [ ] Research prioritizes official vendor documentation consistently
- [ ] Coverage assessment uses PRP template requirements as baseline
- [ ] Final PRPs demonstrate comprehensive requirement coverage

---

## Anti-Patterns to Avoid

- ❌ Don't compromise official source prioritization for speed - quality over quantity
- ❌ Don't continue iterations indefinitely - implement proper stopping criteria
- ❌ Don't generate generic questions when gaps are specific - target identified gaps
- ❌ Don't ignore existing research service patterns - build on proven foundation  
- ❌ Don't skip coverage validation - ensure comprehensive requirement gathering
- ❌ Don't treat all gaps equally - prioritize critical business and technical requirements
- ❌ Don't cache research results indefinitely - implement appropriate cache invalidation
- ❌ Don't break existing API contracts - maintain backward compatibility