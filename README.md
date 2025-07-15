# Spatial Jobs Index

A web application for visualizing employment access data in the Dallas-Fort Worth area, helping policymakers and researchers understand job accessibility patterns across the region.

## Overview

The Spatial Jobs Index provides interactive maps showing:
- Job accessibility by occupation category
- Employment opportunities by wage level
- Transit-based travelshed analysis

This project is developed by Dallas College LMIC (Labor Market Information Center) to support data-driven workforce development decisions.

## Quick Start

### Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- PostgreSQL with PostGIS extension (for backend development)

### Running the Application

```bash
# Clone the repository
git clone https://github.com/Dallas-College-LMIC/spatial-jobs-index.git
cd spatial-jobs-index

# Enter the development environment
nix develop

# Run both backend and frontend
nix run
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Environment Setup

### Backend Configuration
Create `backend/.env` with your database credentials:
```
USERNAME=your_postgres_user
PASS=your_postgres_password
URL=your_postgres_host
DB=your_postgres_database
```

### Frontend Configuration
For local development, create `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Building for Production

```bash
# Build backend Docker image
nix build .#backend-docker

# Build frontend for deployment
nix build .#frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

For detailed technical documentation and coding standards, see [AGENTS.md](./AGENTS.md).

## Project Structure

- `backend/` - FastAPI REST API serving spatial job data
- `frontend/` - Interactive web application with maps
- `flake.nix` - Nix configuration for reproducible builds

## License

[Add your license information here]

## Acknowledgments

- Dallas College LMIC for project sponsorship
- Contributors and maintainers

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/Dallas-College-LMIC/spatial-jobs-index/issues) page.
