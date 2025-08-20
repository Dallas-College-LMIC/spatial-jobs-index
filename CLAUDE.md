# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spatial Jobs Index is a full-stack web application for visualizing job accessibility data in the Dallas-Fort Worth area. It consists of:
- **Backend**: Python/FastAPI REST API with PostGIS spatial data
- **Frontend**: TypeScript/Vite web app with Mapbox GL maps
- **Infrastructure**: Nix-based reproducible development environment

## Essential Development Commands

Run the following to get commands:
```bash
just --list
just --list backend
just --list frontend
```

### Running Frontend and Backend
```bash
# Run both
just run

# Kill both
just stop
```
### Backend Development
```bash
# Run tests
just backend::test          # All tests
just backend::unit-test     # Unit tests only

# Code quality
just backend::lint          # Auto-fix linting (ruff)
just backend::format        # Format code
just backend::type-check     # Type checking (mypy)

# Development server
cd backend && uv run python -m uvicorn app.main:app --reload
```

### Frontend Development
```bash
# Run tests
just frontend::test         # Run tests in watch mode
cd frontend && npm run test:run     # Run once
cd frontend && npm run test:coverage # With coverage

# Code quality
just frontend::lint         # ESLint
just frontend::type-check    # TypeScript checking

# Development server
cd frontend && npm run dev
```

### Testing a Single Test
```bash
# Backend - pytest pattern matching
cd backend && pytest -k "test_name_pattern"

# Frontend - Vitest pattern matching
cd frontend && npm run test -- test_name_pattern
```

## Architecture Overview

### Backend Architecture
The backend follows a layered architecture with clear separation of concerns:

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── services.py          # Business logic layer
│   ├── repositories/        # Data access layer
│   │   ├── occupation.py    # Occupation data queries
│   │   └── school_of_study.py # Education data queries
│   └── routers/             # API endpoints
│       ├── occupation.py
│       └── school_of_study.py
```

Key patterns:
- **Repository Pattern**: All database queries go through repository classes
- **Service Layer**: Business logic is separated from API routes
- **Dependency Injection**: FastAPI's DI system for database sessions
- **Async/Await**: Fully async for better performance
- **PostGIS Integration**: Spatial queries for geographic data

### Frontend Architecture
The frontend uses a service-oriented architecture:

```
frontend/
├── src/
│   ├── js/
│   │   ├── controllers/     # UI event handlers
│   │   ├── services/        # Business logic
│   │   │   ├── api/        # Backend API calls
│   │   │   ├── cache/      # Client-side caching
│   │   │   └── ui/         # UI state management
│   │   ├── utils/          # Shared utilities
│   │   └── types/          # TypeScript type definitions
│   └── pages/              # HTML entry points
```

Key patterns:
- **Service Layer**: API, cache, and UI services handle different concerns
- **Type Safety**: Full TypeScript with strict mode
- **Map Integration**: Mapbox GL for interactive visualizations
- **Client Caching**: 24-hour cache for API responses

## Development Workflow

### Git Workflow
```bash
# Create feature branch from master
git checkout -b feature/your-feature-name

# Make changes with TDD approach
# 1. Write failing test
# 2. Implement feature
# 3. Refactor

# Verify quality before commit
just backend::test    # or frontend::test
just backend::lint    # or frontend::lint

# Commit and push
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

### Environment Setup
Backend requires `.env` file:
```env
USERNAME=postgres_user
PASS=postgres_password
URL=postgres_host
DB=postgres_database
```

Frontend requires `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_token
```

## CI/CD Pipeline

GitHub Actions runs automated checks on every push:
1. **Change Detection**: Only runs checks for modified components
2. **Quality Checks**: Linting, type checking, and tests with coverage
3. **Deployment**: Automatic deployment on master branch

Coverage requirements:
- Backend: Enforced through pytest
- Frontend: 70-75% for branches/functions/lines

## Key Technical Details

### API Endpoints
- `/api/occupation/` - Job data by occupation
- `/api/schoolofstudy/` - Education program data
- `/api/jobs/` - Raw job postings
- All endpoints support query parameters for filtering

### Spatial Data
- Uses PostGIS for geographic queries
- Coordinate system: EPSG:4326 (WGS84)
- Travel time calculations based on isochrones
- Census tract-level aggregations

### Performance Optimizations
- Backend: Async SQLAlchemy queries, response caching
- Frontend: 24-hour client cache, lazy loading
- Rate limiting: 60 requests/minute per IP

## Testing Philosophy

Follow Test-Driven Development (TDD):
1. Write failing test first
2. Implement minimal code to pass
3. Refactor while keeping tests green

Test organization:
- Backend: `tests/unit/` and `tests/integration/`
- Frontend: `__tests__/` directories next to source files

Use factories and fixtures for test data setup.
