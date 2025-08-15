# Flask PRP Generator

A Flask-based web application that transforms business ideas into comprehensive Product Requirement Prompts (PRPs) ready for AI agent execution.

## Features

- **Intelligent Questioning**: AI-powered questionnaire generation to extract detailed requirements
- **Automated Research**: Preference for official vendor documentation sources
- **Comprehensive PRP Generation**: Complete PRPs with implementation blueprints and validation loops  
- **Web Interface**: Progressive questionnaire interface for entrepreneurs
- **API Integration**: RESTful APIs for programmatic access
- **Quality Assessment**: Built-in quality metrics and validation

## Architecture

```
flask_prp_wrapper/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── models/                # Pydantic data models
├── services/              # Business logic services
│   ├── questioning_engine.py
│   ├── research_service.py
│   └── prp_generator.py
├── api/                   # REST API endpoints
├── templates/             # Web interface templates
├── static/                # CSS, JavaScript assets
└── utils/                 # PRP system integration utilities
```

## Quick Start

### Development Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Development Server**:
   ```bash
   python run.py
   ```

3. **Access Application**:
   - Web Interface: http://localhost:5000
   - API Documentation: http://localhost:5000/api/v1/status

### Docker Deployment

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Access Application**:
   - Web Interface: http://localhost:8000
   - Health Check: http://localhost:8000/health

## API Usage

### Submit Business Concept

```bash
curl -X POST http://localhost:5000/api/v1/concepts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Restaurant Management System",
    "description": "A comprehensive solution for small restaurants to manage inventory, orders, and customer relationships using AI-powered insights.",
    "domain": "saas",
    "business_model": "subscription"
  }'
```

### Generate Questions

```bash
curl -X POST http://localhost:5000/api/v1/concepts/{concept_id}/questions \
  -H "Content-Type: application/json" \
  -d '{"max_questions": 10}'
```

### Submit Answers

```bash
curl -X POST http://localhost:5000/api/v1/questionnaire/{session_id}/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "q1",
    "answer": "Small restaurant owners with 1-50 employees",
    "confidence_score": 0.9
  }'
```

### Generate PRP

```bash
curl -X POST http://localhost:5000/api/v1/concepts/{concept_id}/generate-prp
```

## Configuration

Environment variables:

- `FLASK_ENV`: `development` | `production` | `testing`
- `SECRET_KEY`: Flask secret key (required in production)
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `WEB_SEARCH_API_KEY`: Web search API key (optional)

## Research Service Configuration

The research service prioritizes official vendor documentation:

1. **Official Documentation Sites** (Highest Priority)
   - docs.python.org
   - flask.palletsprojects.com
   - docs.aws.amazon.com
   - etc.

2. **Official GitHub Repositories** 
3. **Stack Overflow**
4. **Other Sources** (Lowest Priority)

## Quality Metrics

Generated PRPs are assessed on:
- **Content Completeness** (0-10): Presence of all required sections
- **Context Richness** (0-10): Quality and quantity of research context
- **Validation Coverage** (0-10): Executable validation commands
- **Technical Depth** (0-10): Implementation detail and patterns

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=flask_prp_wrapper --cov-report=term-missing

# Run linting
ruff check flask_prp_wrapper/

# Run type checking
mypy flask_prp_wrapper/ --ignore-missing-imports
```

## Validation Loop

The generated PRPs include a comprehensive validation loop:

### Level 1: Syntax & Style
```bash
ruff check src/ --fix
mypy src/
ruff format src/
```

### Level 2: Unit Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

### Level 3: Integration Testing
```bash
python main.py &
curl -f http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/test -d '{"test": "data"}'
```

## Integration with PRPs-agentic-eng

The Flask wrapper integrates with the existing PRP system:

- Saves generated PRPs to `PRPs/` directory
- Uses existing `PRPs/scripts/prp_runner.py` for execution
- Follows established PRP template structure
- Maintains compatibility with existing validation commands

## Production Deployment

1. **Set Environment Variables**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY="your-secret-key-here"
   export DATABASE_URL="postgresql://user:pass@localhost/db"
   ```

2. **Use Production Database**:
   - PostgreSQL recommended for production
   - Redis recommended for session storage

3. **Security Considerations**:
   - Enable HTTPS in production
   - Set secure session cookies
   - Configure proper CORS policies
   - Use environment variables for sensitive data

## Contributing

1. Follow the PRP methodology for new features
2. Maintain compatibility with existing PRP system
3. Include comprehensive tests
4. Update documentation

## License

This project integrates with the PRPs-agentic-eng framework and follows its licensing terms.