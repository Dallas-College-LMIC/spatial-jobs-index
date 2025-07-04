# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this monorepo.

## IMPORTANT: Serena MCP Usage Instructions

**ALWAYS activate the appropriate Serena project when working with code:**
- When editing ANY file in `backend/`: First run `mcp__serena__activate_project` with "backend"
- When editing ANY file in `frontend/`: First run `mcp__serena__activate_project` with "frontend"
- Use Serena's language-aware tools INSTEAD of basic tools:
  - `mcp__serena__find_symbol` instead of Grep for finding classes/functions/methods
  - `mcp__serena__replace_symbol_body` instead of Edit for changing function/class implementations
  - `mcp__serena__insert_before_symbol`/`mcp__serena__insert_after_symbol` for adding new code
  - `mcp__serena__get_symbols_overview` instead of Read for understanding file structure
  - `mcp__serena__find_referencing_symbols` to find where code is used
  - `mcp__serena__replace_regex` for complex multi-line replacements

**Example workflow when asked to modify backend code:**
1. First: `mcp__serena__activate_project("backend")`
2. Then: Use Serena tools for all code operations
3. Only use basic Read/Edit/Grep for non-code files (configs, docs)

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

### Serena MCP Server
Serena provides language-aware code intelligence for navigating and editing code:
- **Projects**: Backend and frontend are configured as separate Serena projects
- **Switching projects**: Use `activate_project` with "backend" or "frontend"
- **Key features**:
  - Symbol-based navigation and editing (find/replace symbols, not just text)
  - Language server integration for Python and TypeScript
  - Project memories for storing important context
  - Intelligent code search and refactoring

### Other MCP Servers
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

The monorepo uses GitHub Actions workflows located in `.github/workflows/`:

### CI Workflow (`ci.yml`)
- **Path-based execution**: Only runs tests for components that changed
- **Granular filters**: 
  - Backend changes trigger Python tests, linting, and type checking
  - Frontend changes trigger npm tests and Nix build verification
  - Documentation-only changes skip CI entirely
- **Cachix integration**: All Nix builds use shared cache for speed
- **Coverage reporting**: Uploads to Codecov with component-specific flags

### Deploy Workflow (`deploy.yml`)
- **Triggered by**: Successful CI completion on main branch
- **Backend deployment**:
  - Builds Docker image with Nix
  - Pushes to GitHub Container Registry
  - Deploys to VPS via SSH
- **Frontend deployment**:
  - Builds static site with Nix
  - Deploys to GitHub Pages

### Required GitHub Secrets
- `CACHIX_AUTH_TOKEN`: For Nix build caching
- `GHCR_TOKEN`: For pushing Docker images
- `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`: For backend deployment

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

## MCP Server Configuration

### Serena MCP Server (MUST USE FOR CODE EDITING)
**Critical**: Serena provides language-aware code intelligence that is REQUIRED for code editing:
- **Projects configured**: 
  - "backend" - Python/FastAPI code in backend/
  - "frontend" - TypeScript/Vite code in frontend/
- **Activation is MANDATORY**: Always run `mcp__serena__activate_project` before editing code
- **Tool priority**:
  1. ALWAYS use Serena tools for code operations
  2. ONLY use basic Read/Edit/Grep for non-code files (JSON, YAML, Markdown)
- **Key capabilities**:
  - Symbol-based navigation (finds exact definitions, not just text matches)
  - Language server integration (understands imports, types, references)
  - Intelligent refactoring (safely rename across files)
  - Project memories (stores important context between sessions)

### Other MCP Servers
- **context7**: Use for up-to-date library documentation
- **nixos**: Use for Nix package/option queries
- **browsermcp**: Use for browser automation tasks

## Best Practices

1. **ALWAYS activate Serena first** when working on code in backend/ or frontend/
2. Use context7 to fetch current documentation during implementation
3. Run linting and type checking before committing
4. Follow existing code patterns - use Serena's `get_symbols_overview` to understand structure
5. Update this file when adding new workflows