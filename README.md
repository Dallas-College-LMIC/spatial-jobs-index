# Spatial Jobs Index

A monorepo containing the Spatial Jobs Index API (backend) and web application (frontend) for visualizing employment access data in the Dallas-Fort Worth area.

## Architecture

- **Backend**: Python 3.13 FastAPI application with PostgreSQL/PostGIS for spatial data
- **Frontend**: TypeScript/Vite web application with Mapbox GL JS for interactive maps

## Quick Start

### Prerequisites

- Nix with flakes enabled
- PostgreSQL with PostGIS extension (for backend)

### Development

```bash
# Enter the development shell with all tools
nix develop

# Or enter specific development shells
nix develop .#backend   # Backend-only environment
nix develop .#frontend  # Frontend-only environment
```

### Running the Applications

```bash
# Run both backend and frontend
nix run

# Run individual services
nix run .#backend   # API server on http://localhost:8000
nix run .#frontend  # Dev server on http://localhost:5173
```

### Building

```bash
# Build the backend package
nix build .#backend

# Build the frontend for production
nix build .#frontend

# Build the backend Docker image
nix build .#backend-docker
```

## Project Structure

```
spatial-jobs-index/
├── flake.nix           # Nix flake configuration
├── flake.lock          # Lock file for reproducible builds
├── README.md           # This file
├── backend/            # FastAPI backend application
│   ├── app/            # Application code
│   ├── tests/          # Test suite
│   ├── pyproject.toml  # Python project configuration
│   └── uv.lock         # Python dependency lock file
└── frontend/           # Vite frontend application
    ├── src/            # Source code
    ├── public/         # Static assets
    ├── package.json    # Node.js project configuration
    └── vite.config.ts  # Vite configuration
```

## Backend API

The backend provides RESTful endpoints for spatial job data:

- `/occupation_ids` - List available occupation categories
- `/geojson` - Spatial data as GeoJSON with job metrics
- `/occupation_data/{category}` - Spatial data for specific occupations

See [backend/README.md](backend/README.md) for detailed API documentation.

## Frontend Application

The frontend provides interactive visualizations:

- **Landing Page** (`index.html`) - Project information
- **Occupation Map** (`access_occupation.html`) - Job access by occupation
- **Wage Level Map** (`access_wagelvl.html`) - Job access by wage level

See [frontend/README.md](frontend/README.md) for detailed frontend documentation.

## Environment Variables

### Backend
- `USERNAME` - Database username
- `PASS` - Database password  
- `URL` - Database host URL
- `DB` - Database name

### Frontend
- `VITE_API_BASE_URL` - Backend API URL (defaults to http://localhost:8000)

## Development Workflow

### Backend Development

```bash
cd backend
uv run python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker Deployment (Backend)

```bash
# Build Docker image
nix build .#backend-docker

# Load image into Docker
docker load < result

# Run container
docker run -p 8000:8000 spatial-jobs-index-api:latest
```

### Static Deployment (Frontend)

```bash
# Build frontend
nix build .#frontend

# Deploy the result/ directory to your static host
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

See individual project CLAUDE.md files for AI-assisted development guidelines.

## License

[Add your license information here]
