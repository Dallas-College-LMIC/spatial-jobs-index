# Dallas-Fort Worth Spatial Jobs Index (SJI) WebApp

## Overview

The SJI WebApp is an interactive mapping application that visualizes employment access data for the Dallas-Fort Worth metropolitan area. Built for Dallas College LMIC (Labor Market Information Center), this tool helps analyze transit travelshed indices and job accessibility patterns across census tracts.

## Features

- **Interactive Maps**: Visualize employment access data using Mapbox GL JS
- **Occupation-Based Analysis**: Search and filter job access by specific occupations (~800 occupation codes)
- **Wage Level Analysis**: View job accessibility patterns by wage categories
- **Data Export**: Download GeoJSON data for further analysis
- **Performance Optimized**: Client-side caching reduces API calls by ~99%
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## Technology Stack

- **Framework**: Vue 3.5.18 with Composition API
- **Build System**: Vite 6.3.5
- **Language**: TypeScript 5.8.3 (strict mode)
- **State Management**: Pinia 3.0.3
- **Routing**: Vue Router 4.5.1
- **Mapping**: Mapbox GL JS with @studiometa/vue-mapbox-gl
- **UI Framework**: Bootstrap 5.0.0-beta2 (CSS only)
- **Testing**: Vitest 3.2.3 with Vue Test Utils
- **Package Manager**: npm

## Quick Start

### Prerequisites

- Node.js 18+
- npm 9+
- A Mapbox API token (set in environment variables)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Dallas-College-LMIC/sji-webapp.git
cd sji-webapp
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Configure your environment variables:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Testing

```bash
# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Generate coverage report
npm run test:coverage

# Open Vitest UI
npm run test:ui
```

## Project Structure

```
sji-webapp/
|-- index.html                 # Landing page
|-- access_occupation.html     # Occupation-based map
|-- access_wagelvl.html        # Wage level map
|-- access_school_of_study.html # School of study map
|-- travel_time.html          # Travel time analysis
|-- src/
|   |-- vue/                  # Vue 3 application
|   |   |-- components/       # Vue components
|   |   |   |-- common/       # Shared components
|   |   |   |-- display/      # Display components
|   |   |   |-- forms/        # Form components
|   |   |   `-- map/          # Map-related components
|   |   |-- composables/      # Vue composables
|   |   |-- stores/           # Pinia stores
|   |   |-- router/           # Vue Router configuration
|   |   |-- pages/            # Page components
|   |   `-- main.ts          # Vue app entry point
|   |-- js/                   # Legacy TypeScript (being migrated)
|   |   |-- services/         # Service layers
|   |   `-- utils/            # Utilities
|   |-- styles/              # CSS files
|   |-- types/               # TypeScript type definitions
|   `-- __tests__/           # Test suite
|-- public/                  # Static assets
`-- vite.config.ts          # Vite configuration
```

## Vue 3 Architecture

### State Management with Pinia

The application uses Pinia stores for centralized state management:

- **`occupationStore`**: Manages occupation data, selection, and caching
- **`schoolOfStudyStore`**: Handles school of study data and selection
- **`mapStore`**: Controls map instance, layers, and interactions
- **`uiStore`**: Manages UI state, modals, and notifications

### Component Organization

Components follow a hierarchical structure:

- **Pages**: Top-level route components (`OccupationPage.vue`, `HomePage.vue`)
- **Common**: Shared components (`AppHeader.vue`, `Navigation.vue`, `LoadingSpinner.vue`)
- **Forms**: Input components (`OccupationSelect.vue`, `SearchForm.vue`, `FilterControls.vue`)
- **Display**: Data presentation (`DataTable.vue`, `Legend.vue`, `StatsPanel.vue`)
- **Map**: Map-specific components (`MapContainer.vue`, `MapControls.vue`, `OccupationMap.vue`)

### Composables

Reusable composition functions for common logic:

- **`useApi`**: Base API composable with error handling
- **`useMapbox`**: Map initialization and lifecycle management
- **`useMapLayers`**: Layer management and visibility control
- **`useMapInteractions`**: Click/hover handlers and popups

### Routing

Vue Router handles navigation with lazy-loaded routes for optimal performance:

- `/` - Home page
- `/occupation` - Occupation analysis
- `/school-of-study` - Education program analysis
- `/wage-level` - Wage level visualization
- `/travel-time` - Travel time analysis

## API Integration

The application expects a backend API that provides:

- `/occupation_ids` - List of available occupation codes
- `/geojson/{occupation_id}` - GeoJSON data for specific occupations
- `/geojson/wage/{wage_level}` - GeoJSON data for wage levels

## Deployment

### GitHub Pages

The project is configured for GitHub Pages deployment:

```bash
npm run deploy
```

This will build the project and deploy to the `gh-pages` branch.

### Environment Configuration

For production deployment:
1. Set `VITE_API_BASE_URL` to your production API endpoint
2. Ensure CORS headers are properly configured on your API
3. Configure your Mapbox token for the production domain

## Performance Features

- **Client-Side Caching**: Occupation IDs are cached for 24 hours using Pinia persistence
- **Non-Blocking Loading**: Maps load immediately while data fetches in background
- **Optimized Bundle**: Advanced code splitting with manual chunks:
  - Vendor chunks: `vue-vendor`, `mapbox-vendor`, `state-vendor`
  - Application chunks: `components`, `stores`, `map-components`
  - Lazy-loaded routes reduce initial bundle size
- **Tree Shaking**: Production builds remove unused code
- **Asset Optimization**: Images under 4KB are inlined, larger assets use content hashing

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing Guidelines

- All new features must include tests
- Maintain 80%+ code coverage
- Run tests before committing
- Use TypeScript strict mode

## License

This project is part of Dallas College LMIC. Please contact the organization for licensing information.

## Acknowledgments

- Dallas College Labor Market Information Center
- Transit accessibility data providers
- Open source community

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact Dallas College LMIC
- Review the [developer documentation](./CLAUDE.md)

---

Built with ❤️ for better employment accessibility analysis in DFW
