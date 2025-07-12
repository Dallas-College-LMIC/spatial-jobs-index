# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this monorepo.

## Monorepo Structure

This is a Nix flake-based monorepo containing:
- **backend/**: Python FastAPI application for spatial jobs data API
- **frontend/**: TypeScript/Vite web application for visualizing the data

## Project Navigation

### Working with Sub-Projects
- Each project has its own CLAUDE.md with project-specific details:
  - `backend/CLAUDE.md` - Backend-specific commands and architecture
  - `frontend/CLAUDE.md` - Frontend-specific commands and architecture
- Use the root CLAUDE.md (this file) for monorepo-level operations
- Navigate to project directories when working on project-specific tasks

### When to Work at Different Levels
- **Monorepo level (root)**:
  - Running both services together
  - Cross-project refactoring
  - Dependency updates affecting both projects
  - CI/CD configuration
- **Project level (backend/frontend)**:
  - Feature implementation within one project
  - Project-specific testing and debugging
  - Project-specific dependency management

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

### Frontend Commands

**Note:** For consistency with the backend, use Nix development shell for all frontend operations.

**Development server:**
```bash
nix develop .#frontend -c bash -c "cd frontend && npm install && npm run dev"
# Or if already in the frontend directory:
nix develop .#frontend
npm install
npm run dev
```

**Build for production:**
```bash
nix build .#frontend
```

### Manual Quality Checks

These commands are useful for:
- Running checks before committing to catch issues early
- Debugging CI failures locally
- Manual code quality verification

#### Backend Quality Checks

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

#### Frontend Quality Checks

**Run tests:**
```bash
nix develop .#frontend -c bash -c "cd frontend && npm test"
```

**Type checking:**
```bash
nix develop .#frontend -c bash -c "cd frontend && npm run type-check"
```

**Lint and format:**
```bash
nix develop .#frontend -c bash -c "cd frontend && npm run lint"
nix develop .#frontend -c bash -c "cd frontend && npm run format"
```

**Coverage report:**
```bash
nix develop .#frontend -c bash -c "cd frontend && npm run test:coverage"
```

## Project Architecture

**Backend (Python/FastAPI):**
- REST API for spatial jobs data
- PostgreSQL with PostGIS for spatial operations
- See `backend/CLAUDE.md` for detailed architecture, endpoints, and configuration

**Frontend (TypeScript/Vite):**
- Interactive maps with Mapbox GL JS
- Client-side caching for performance
- See `frontend/CLAUDE.md` for detailed architecture and component structure

## Cross-Project Coordination

### Adding a New API Endpoint (Full Stack)
When implementing features that span both projects:

1. **Backend Implementation**:
   - Define Pydantic models in `backend/app/models.py`
   - Add service method in `backend/app/services.py`
   - Create endpoint in `backend/app/main.py` with rate limiting
   - Write unit tests in `backend/tests/unit/`
   - Add integration tests in `backend/tests/integration/`

2. **Frontend Integration**:
   - Update frontend API service in `frontend/src/js/api.ts`
   - Add TypeScript types in `frontend/src/types/api.ts`
   - Update UI components to use new endpoint
   - Add frontend tests for new functionality

3. **Testing Full Stack**:
   - Run `nix run` to test both services together
   - Verify CORS configuration for new endpoints
   - Test error handling across the stack

### Parallel Development Workflow
For tasks affecting both projects:
1. Open terminal tabs/panes for each project
2. Run backend: `cd backend && uv run python -m uvicorn app.main:app --reload`
3. Run frontend: `cd frontend && npm run dev`
4. Make changes and see live updates in both services

### Working with the Monorepo

1. Always use `nix develop` for consistent development environment
2. Run `nix flake update` to update dependencies
3. Test all outputs before committing: `nix build .#backend .#frontend`
4. Use `nix run` to test both services together

## Common Development Tasks

For project-specific tasks, refer to:
- Backend tasks: See `backend/CLAUDE.md`
- Frontend tasks: See `frontend/CLAUDE.md`

## MCP Server Setup

This project uses several MCP (Model Context Protocol) servers configured in `.mcp.json`:

### MCP Servers
- **context7**: Fetches up-to-date documentation for libraries and frameworks
- **nixos**: Provides Nix ecosystem information (packages, options, flakes)
- **browsermcp**: Browser automation capabilities

## Best Practices

- Use the context7 MCP tool to fetch up-to-date documentation for libraries and frameworks during planning, implementation, and debugging
- Use the nixos MCP tool for Nix-related queries (packages, options, flakes, home-manager, darwin configurations)
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

## CI/CD Workflows

The monorepo uses a three-stage GitHub Actions pipeline located in `.github/workflows/`:

### Workflow Chain
```
Push to master → CI (tests) → Build (artifacts) → Deploy (services)
```

### CI Workflow (`ci.yml`)
- **Purpose**: Runs tests and quality checks only
- **Path-based execution**: Only runs tests for components that changed
- **Granular filters**:
  - Backend changes trigger Python tests, linting, and type checking
  - Frontend changes trigger npm tests and type checking
  - Documentation-only changes skip CI entirely
- **Coverage reporting**: Uploads to Codecov with component-specific flags
- **On success**: Triggers the Build workflow

### Build Workflow (`build.yml`)
- **Purpose**: Builds deployable artifacts after CI passes
- **Triggered by**: Successful CI completion
- **Backend build**:
  - Builds Docker image with Nix
  - Verifies image was created successfully
- **Frontend build**:
  - Builds static site with Nix
  - Verifies all expected files exist
- **Cachix integration**: All builds are cached for deployment
- **Both builds must succeed**: Workflow fails if either build fails

### Deploy Workflow (`deploy.yml`)
- **Purpose**: Deploys pre-built artifacts to production
- **Triggered by**: Successful Build completion
- **Backend deployment**:
  - Pulls Docker image from Cachix
  - Pushes to GitHub Container Registry
  - Deploys to VPS via SSH
- **Frontend deployment**:
  - Pulls static site from Cachix
  - Deploys to GitHub Pages
- **No building**: All artifacts come from Cachix

### Required GitHub Secrets
- `CACHIX_AUTH_TOKEN`: For Nix build caching
- `GHCR_TOKEN`: For pushing Docker images
- `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`: For backend deployment

## Deployment

### Manual Deployment (Local Testing)

**Backend Docker:**
```bash
nix build .#backend-docker
docker load < result
docker run -p 8000:8000 spatial-jobs-index-api:latest
```

**Frontend Static Site:**
```bash
nix build .#frontend
# Deploy result/ directory to static host
```

### Automated Deployment
Deployment happens automatically via GitHub Actions:
1. Push to master branch
2. CI runs tests and quality checks
3. Build workflow creates deployable artifacts
4. Deploy workflow pushes to production

See the [CI/CD Workflows](#cicd-workflows) section for details.

## Debugging Tips

- Backend: Check `htmlcov/index.html` for coverage reports
- Frontend: Use Vitest UI with `npm run test:ui`
- Both: Check respective `node_modules/` or Python env for dependency issues
- Use `nix develop .#backend` or `nix develop .#frontend` for isolated debugging

## MCP Server Configuration

- **context7**: Use for up-to-date library documentation
- **nixos**: Use for Nix package/option queries
- **browsermcp**: Use for browser automation tasks
- **postgres**: Database analysis and optimization tools for PostgreSQL
  - Health monitoring: Check indexes, vacuum status, connections
  - Query optimization: Analyze execution plans and suggest indexes
  - Schema exploration: List tables, views, and their structures

## Pre-commit Hooks Setup

This project uses the pre-commit framework to automatically run tests and quality checks before commits.

### Initial Setup

1. **Install pre-commit hooks** (run this once after cloning):
   ```bash
   # In the Nix development shell
   pre-commit install
   ```

2. **Verify installation**:
   ```bash
   # This should show .git/hooks/pre-commit exists
   ls -la .git/hooks/pre-commit
   ```

### What Runs on Commit

The pre-commit hooks automatically run the following checks on changed files:

**General (all files):**
- Remove trailing whitespace
- Fix end-of-file newlines
- Check for merge conflicts
- Prevent large files (>5MB)
- Validate YAML/JSON/TOML syntax

**Backend (Python files):**
- Ruff linting with auto-fix
- MyPy type checking
- Unit tests (fast tests only)

**Frontend (TypeScript/JavaScript files):**
- ESLint
- TypeScript type checking
- Vitest unit tests

### Usage

1. **Normal commits** - hooks run automatically:
   ```bash
   git add .
   git commit -m "Your message"
   # Pre-commit runs here
   ```

2. **Skip hooks when necessary** (use sparingly):
   ```bash
   git commit --no-verify -m "Emergency fix"
   ```

3. **Run hooks manually on all files**:
   ```bash
   pre-commit run --all-files
   ```

4. **Run specific hook**:
   ```bash
   pre-commit run backend-unit-tests
   pre-commit run frontend-lint
   ```

5. **Update hook versions**:
   ```bash
   pre-commit autoupdate
   ```

### Troubleshooting

- **"node_modules not found"**: Run `npm install` in the frontend directory
- **Python import errors**: Ensure you're in the Nix shell (`nix develop`)
- **Hooks not running**: Run `pre-commit install` again
- **See what hooks would run**: `pre-commit run --dry-run`

### Hook Configuration

The configuration is in `.pre-commit-config.yaml`. Custom scripts are in `scripts/pre-commit/`.

## Best Practices

1. Use context7 to fetch current documentation during implementation
2. Run linting and type checking before committing (automated by pre-commit)
3. Follow existing code patterns
4. Update this file when adding new workflows
5. Use pre-commit hooks to catch issues early
