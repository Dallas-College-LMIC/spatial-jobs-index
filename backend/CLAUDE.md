# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the backend project.

## Parent Context
This is part of a monorepo. See the root `../CLAUDE.md` for:
- Monorepo-wide commands and workflows
- Cross-project coordination
- Full stack development patterns

## Development Commands
If working without Nix or inside the dev shell:
```bash
cd backend
uv run python -m uvicorn app.main:app --reload
```

**Linting and auto-fix:**
```bash
ruff check
ruff check --fix
```

**Type checking:**
```bash
mypy app/
```

**Running tests:**
```bash
# Run all tests with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_services.py -v

# Run with coverage in terminal
uv run pytest --cov=app --cov-report=term-missing

# Stop on first failure
uv run pytest -x

# Run tests with verbose output for debugging
uv run pytest -vv

# Run only integration tests
uv run pytest tests/integration/ -v

# Run tests matching a specific pattern
uv run pytest -k "test_rate_limiting" -v
```

## Architecture

This is a FastAPI-based spatial jobs index API that provides endpoints for job market data visualization.

**Tech Stack:**
- Python 3.13+ with FastAPI framework
- PostgreSQL with PostGIS extension for spatial data
- SQLAlchemy ORM with GeoAlchemy2 for spatial operations
- Pydantic for data validation and response models
- Nix flake for reproducible builds and Docker packaging

**Core Structure:**
- `app/main.py`: Main FastAPI application with CORS, rate limiting, and API endpoints
- `app/models.py`: SQLAlchemy ORM models and Pydantic response models
- `app/database.py`: Database configuration with connection pooling and session management
- `app/services.py`: Business logic layer with service classes (OccupationService, SpatialService)
- Clean architecture pattern with separation of concerns
- No authentication required (public API)

**Database Configuration:**
- PostgreSQL with PostGIS for spatial data (jsi_data schema)
- Connection pooling: pool_size=10, max_overflow=20, pool_pre_ping=True
- DatabaseConfig class for environment variable validation

**Key Database Tables:**
- `jsi_data.occupation_lvl_data`: Job occupation data by category
  - Primary keys: geoid, category
  - Columns: openings_2024_zscore, jobs_2024_zscore, openings_2024_zscore_color, geom
- `jsi_data.tti_clone`: Spatial data with z-scores for job metrics and PostGIS geometry (primary key: geoid)
  - Columns: all_jobs_zscore, all_jobs_zscore_cat, living_wage_zscore, living_wage_zscore_cat, not_living_wage_zscore, not_living_wage_zscore_cat, geom

**Security:**
- Rate limiting via SlowAPI (10-30 requests/minute per endpoint)
- CORS configured for specific allowed origins including Vite dev server (localhost:5173)
- Environment variable validation on startup using Pydantic
- Database connection health checks with pool_pre_ping

**Current Active Endpoints:**
- `/occupation_ids`: List all available occupation categories
- `/geojson`: Return spatial data as GeoJSON with job metrics (Content-Type: application/geo+json)
- `/occupation_data/{category}`: Return spatial data for a specific occupation category (Content-Type: application/geo+json)

**Deprecated/Commented Endpoints:**
- `/items/{category_type}`: Get job data by category type (currently commented out)
- `/occupations/{occupation_id}`: Get specific occupation data (currently commented out)

**Environment Variables Required:**
- `USERNAME`, `PASS`: Database credentials
- `URL`, `DB`: Database connection details

**Response Models:**
- Pydantic models for structured JSON responses
- GeoJSON-specific models: SpatialFeatureProperties, GeoJSONFeature, GeoJSONFeatureCollection
- Type safety and automatic OpenAPI documentation generation

## Development Environment

**Nix Shell Environment:**
- Python 3.13 with all dependencies
- Development tools: mypy, ruff, python-lsp-server, debugpy
- Environment variables: UV_PYTHON_DOWNLOADS=never, UV_PYTHON set to Nix Python

**Python Dependencies (pyproject.toml):**
- Main: fastapi, uvicorn, sqlalchemy, geoalchemy2, psycopg2-binary, pydantic, python-dotenv, slowapi, geojson
- Development: mypy, ruff, python-lsp-server, debugpy
- Testing: pytest, pytest-cov, pytest-asyncio, httpx, faker, factory-boy

**Installing Dependencies:**
```bash
# Install all dependencies (main + dev + test)
uv sync

# Install only test dependencies
uv sync --group test
```

## Deployment

**GitHub Actions CI/CD:**
- Automated builds on push to main branch
- Runs test suite with coverage reporting
- Uses Nix for reproducible Docker builds
- Pushes to GitHub Container Registry: `ghcr.io/dallas-college-lmic/spatial-jobs-index-api:latest`
- Cachix integration for build caching
- Test action workflow for automated testing on pull requests

**Docker Configuration:**
- Port: 8000
- Working directory: /app
- Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Testing

**Test Structure:**
- `tests/unit/`: Unit tests for individual modules (database, models, services, main)
- `tests/integration/`: End-to-end API integration tests
- `tests/test_infrastructure.py`: Test infrastructure verification
- `tests/test_example_endpoints.py`: Example endpoint tests with mocking
- `tests/conftest.py`: Shared test fixtures and configuration
- `tests/factories.py`: Test data factories using factory-boy for generating test data

**Test Coverage:**
- Current coverage: 98% for all application code (startup code and exception handlers excluded)
- HTML coverage reports generated in `htmlcov/`
- SQLite in-memory database used for test isolation
- Some tests skipped when PostgreSQL with PostGIS is required

**Test Features:**
- Comprehensive mocking of database operations
- Rate limiting and CORS testing
- Performance and concurrent request testing
- Error handling and edge case coverage
- Async and sync test client support

**Common Test Patterns:**
```python
# Mock service methods to avoid database dependencies
with patch.object(OccupationService, 'get_occupation_ids') as mock_service:
    mock_service.return_value = ["Test Data"]
    response = test_client.get("/occupation_ids")
```

**Important Notes:**
- Tests use SQLite instead of PostgreSQL, so schema-specific features are mocked
- Rate limiter state is reset between tests to avoid interference
- All database sessions are properly rolled back after each test

## Common Development Tasks

**Adding a New Endpoint:**
1. Define Pydantic models in `app/models.py` for request/response
2. Add service method in `app/services.py` for business logic
3. Create endpoint in `app/main.py` with proper rate limiting
4. Write unit tests in `tests/unit/`
5. Add integration tests in `tests/integration/`

**Database Schema Changes:**
1. Update SQLAlchemy models in `app/models.py`
2. Update test fixtures in `tests/conftest.py` if needed
3. Consider migration strategy for production database

**Best Practices:**
- Always run `ruff check --fix` before committing
- Maintain 100% test coverage for new code
- Use type hints for all function parameters and returns
- Mock external dependencies in unit tests
- Document any new environment variables in this file
- Follow existing code patterns and conventions

**Debugging Tips:**
- Use `pytest -vv` for verbose test output
- Check `htmlcov/index.html` for detailed coverage reports
- SQLite test errors often indicate schema mismatch issues
- Rate limit errors in tests may need limiter reset

## Database Analysis

The postgres MCP server is available for database analysis tasks:
- **Performance**: Analyze query execution plans and get index recommendations
- **Health monitoring**: Check database health, indexes, vacuum status
- **Schema exploration**: List and inspect database objects
- **Query analysis**: Find slow queries and performance bottlenecks

Use these tools when debugging performance issues or planning database optimizations.