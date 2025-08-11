# Current Functionality Documentation
## Pre-Vue 3 Migration Baseline

**Date**: 2025-08-11
**Purpose**: Document existing functionality for regression testing after Vue 3 migration

## Application Pages

### 1. Home Page (`index.html`)
- Landing page with navigation to different map visualizations
- Links to occupation, school of study, wage level, and travel time maps

### 2. Occupation Access Map (`access_occupation.html`)
- **URL**: `/access_occupation.html`
- **Features**:
  - Interactive Mapbox GL map centered on Dallas-Fort Worth
  - Occupation search dropdown (Select2-based)
  - Data visualization by census tracts
  - Color-coded job accessibility layers
  - Popup information on map click
  - Legend for data interpretation
  - Loading states and error handling

### 3. School of Study Map (`access_school_of_study.html`)
- **URL**: `/access_school_of_study.html`
- **Features**:
  - Interactive map for education program data
  - School/program search functionality
  - Census tract-based data visualization
  - Popups with detailed information
  - Data caching for performance

### 4. Wage Level Map (`access_wagelvl.html`)
- **URL**: `/access_wagelvl.html`
- **Features**:
  - Wage data visualization by geographic area
  - Filter by wage levels
  - Interactive map layers
  - Statistical information display

### 5. Travel Time Map (`travel_time.html`)
- **URL**: `/travel_time.html`
- **Features**:
  - Travel time isochrones
  - Multiple time intervals (15, 30, 45, 60 minutes)
  - Origin point selection
  - Transit vs driving time comparison

## Core Functionality

### Map Features
- **Base Map**: Mapbox GL v3.14.0 with street/satellite views
- **Zoom Controls**: Standard zoom in/out buttons
- **Navigation**: Pan, rotate, and tilt capabilities
- **Popups**: Click-triggered information display
- **Legends**: Dynamic color-scale legends
- **Responsiveness**: Mobile and desktop layouts

### Data Features
- **API Integration**: FastAPI backend at `/api/`
- **Caching**: 24-hour client-side cache (localStorage)
- **Error Handling**: Network error recovery and user notifications
- **Loading States**: Visual indicators during data fetch

### Search & Filter
- **Select2 Dropdowns**: Enhanced search with autocomplete
- **Data Filtering**: Client and server-side filtering
- **Search History**: Recent searches cached

### Performance
- **Lazy Loading**: Data loaded on demand
- **Request Optimization**: Debounced search, cached responses
- **Bundle Size**: Current production build ~2.5MB

## API Endpoints Used

1. **Occupation Data**
   - `GET /api/occupation/`
   - Query params: `id`, `name`, `limit`

2. **School of Study Data**
   - `GET /api/schoolofstudy/`
   - Query params: `id`, `program`, `limit`

3. **Wage Data**
   - `GET /api/wages/`
   - Query params: `level`, `tract`

4. **Travel Time Data**
   - `GET /api/traveltime/`
   - Query params: `origin`, `mode`, `time`

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Known Issues & Limitations
1. Select2 dropdowns may not be fully accessible
2. Map controls lack keyboard navigation
3. No offline support
4. Limited mobile gesture support
5. Cache invalidation is time-based only

## Testing Coverage
- Unit Tests: 380 tests passing
- Coverage: 81% statements, 85% branches
- E2E Tests: Not yet implemented
- Performance Tests: Basic caching tests only

## Dependencies
- **Runtime**: jQuery 3.6, Bootstrap 5, Mapbox GL 3.14, Select2 4.1
- **Build**: Vite, TypeScript 5.8
- **Testing**: Vitest 3.2, Testing Library

## Regression Testing Checklist

### Visual Regression
- [ ] Map renders correctly on all pages
- [ ] Popups display with correct formatting
- [ ] Legends show appropriate color scales
- [ ] Loading spinners appear during data fetch
- [ ] Error messages display appropriately

### Functional Regression
- [ ] Search dropdowns populate with data
- [ ] Map interactions (click, zoom, pan) work
- [ ] Data filters apply correctly
- [ ] API calls succeed with correct parameters
- [ ] Cache operates for 24 hours
- [ ] Navigation between pages works

### Performance Regression
- [ ] Initial load time < 3 seconds
- [ ] API response time < 500ms
- [ ] Map interaction remains smooth (60fps)
- [ ] Memory usage stable over time
- [ ] Bundle size < 3MB

### Accessibility Regression
- [ ] Tab navigation through controls
- [ ] Screen reader announcements
- [ ] Color contrast ratios maintained
- [ ] Focus indicators visible

## Success Metrics
- All existing features work identically or better
- No degradation in performance metrics
- Test coverage maintained or improved
- Zero user-facing breaking changes
