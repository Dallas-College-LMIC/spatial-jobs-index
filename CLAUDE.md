# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this monorepo.

## Monorepo Structure

This is a Nix flake-based monorepo containing:
- **backend/**: Python FastAPI application for spatial jobs data API
- **frontend/**: TypeScript/Vite web application for visualizing the data

## Development Commands

### Monorepo Commands

```bash
# Enter combined development shell
nix develop

# Run both services
nix run

# Build all packages
nix build .#backend
nix build .#frontend
nix build .#backend-docker
```

### Backend Commands

**Note:** On NixOS systems, prefix commands with `nix develop -c` or enter a nix shell first.

**Development server:**
```bash
cd backend
uv run python -m uvicorn app.main:app --reload
# Or in nix shell: python -m uvicorn app.main:app --reload
```

**Linting and auto-fix:**
```bash
nix develop -c ruff check backend/
nix develop -c ruff check backend/ --fix
```

**Type checking:**
```bash
nix develop -c mypy backend/app/
```

**Running tests:**
```bash
cd backend
uv run pytest --cov=app --cov-report=html
```

### Frontend Commands

**Development server:**
```bash
cd frontend
npm install
npm run dev
```

**Build for production:**
```bash
cd frontend
npm run build
```

**Run tests:**
```bash
cd frontend
npm test
```

**Lint and format:**
```bash
cd frontend
npm run lint
npm run format
```

## Backend Architecture

**Tech Stack:**
- Python 3.13+ with FastAPI framework
- PostgreSQL with PostGIS extension for spatial data
- SQLAlchemy ORM with GeoAlchemy2 for spatial operations
- Pydantic for data validation and response models
- Nix flake with uv2nix for reproducible builds

**Current Active Endpoints:**
- `/occupation_ids`: List all available occupation categories
- `/geojson`: Return spatial data as GeoJSON with job metrics
- `/occupation_data/{category}`: Return spatial data for a specific occupation category

**Environment Variables Required:**
- `USERNAME`, `PASS`: Database credentials
- `URL`, `DB`: Database connection details

## Frontend Architecture

**Tech Stack:**
- Vite 6.3.5 build system with ES6 modules
- TypeScript 5.8.3 with strict mode
- Mapbox GL JS v1.12.0 for interactive maps
- Bootstrap 5.0.0-beta2 for UI
- Select2 4.1.0 for searchable dropdowns
- Vitest 3.2.3 for testing

**Key Features:**
- Client-side caching with 24-hour TTL for occupation IDs
- Non-blocking data loading for improved UX
- Choropleth maps with z-score based coloring
- Export functionality for GeoJSON data

**Environment Variables:**
- `VITE_API_BASE_URL`: Backend API URL (defaults to http://localhost:8000)

## Common Development Tasks

### Adding a New API Endpoint

1. Define Pydantic models in `backend/app/models.py`
2. Add service method in `backend/app/services.py`
3. Create endpoint in `backend/app/main.py` with rate limiting
4. Write unit tests in `backend/tests/unit/`
5. Add integration tests in `backend/tests/integration/`
6. Update frontend API service in `frontend/src/js/api.ts`
7. Add TypeScript types in `frontend/src/types/api.ts`

### Updating the Frontend Build

1. Make changes in `frontend/src/`
2. Run tests: `cd frontend && npm test`
3. Build: `cd frontend && npm run build`
4. Test the production build locally

### Working with the Monorepo

1. Always use `nix develop` for consistent development environment
2. Run `nix flake update` to update dependencies
3. Test all outputs before committing: `nix build .#backend .#frontend`
4. Use `nix run` to test both services together

## Best Practices

- Always run linting and type checking before committing
- Maintain test coverage above 90% for both projects
- Use type hints in Python and strict TypeScript
- Follow existing code patterns and conventions
- Document any new environment variables
- Update this file when adding new development workflows

## Testing Strategy

### Backend Testing
- Use SQLite in-memory database for unit tests
- Mock external services and database operations
- Test rate limiting and CORS configuration
- Ensure all endpoints have integration tests

### Frontend Testing
- Use Vitest with Happy-DOM for fast testing
- Mock Mapbox GL JS and jQuery/Select2
- Test user interactions and error handling
- Verify caching behavior

## Deployment

### Backend Docker Deployment
```bash
nix build .#backend-docker
docker load < result
docker run -p 8000:8000 spatial-jobs-index-api:latest
```

### Frontend Static Deployment
```bash
nix build .#frontend
# Deploy result/ directory to static host
```

## Debugging Tips

- Backend: Check `htmlcov/index.html` for coverage reports
- Frontend: Use Vitest UI with `npm run test:ui`
- Both: Check respective `node_modules/` or Python env for dependency issues
- Use `nix develop .#backend` or `nix develop .#frontend` for isolated debugging