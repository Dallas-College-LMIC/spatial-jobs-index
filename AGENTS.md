# AGENTS.md

Spatial Jobs Index: DFW employment visualization. Backend: Python/FastAPI/PostgreSQL. Frontend: TypeScript/Vite/Mapbox.

## Quick Start
```bash
nix develop                                           # Enter dev environment
nix run                                              # Run both services
cd backend && uv run pytest                          # Backend tests
cd frontend && npm test                              # Frontend tests
```

## API
- `/occupation_ids` - List occupations
- `/geojson` - All spatial data
- `/occupation_data/{category}` - Filtered spatial data

## Key Files
- `backend/app/models.py` - Database schema
- `backend/app/services.py` - Business logic
- `frontend/src/js/*-main.ts` - Entry points
- `backend/.env.example` - Required env vars

## Notes
- Tests use SQLite, not PostgreSQL
- Frontend caches occupation IDs for 24hr
- Follow existing patterns
