# Vue 3 Migration Plan

This document tracks the progress of migrating the Spatial Jobs Index frontend from vanilla TypeScript to Vue 3.

## Overview
Incremental migration from vanilla TypeScript to Vue 3, organized into 4 phases with detailed subtasks.

## Pre-Migration Tasks
- [ ] Fix current test suite configuration issue
- [ ] Run full test suite and document baseline coverage
- [ ] Create migration branch from current vue3 branch
- [ ] Back up current working application state
- [ ] Document current functionality for regression testing

## Phase 1: Setup & Foundation (Week 1-2)

### 1.1 Core Vue Installation
- [ ] Install Vue 3 core: `npm install vue@^3.5`
- [ ] Install Vite Vue plugin: `npm install -D @vitejs/plugin-vue@^5.2`
- [ ] Install Vue compiler: `npm install -D @vue/compiler-sfc@^3.5`
- [ ] Install Vue TypeScript support: `npm install -D vue-tsc@^2.2`
- [ ] Install Vue TSConfig: `npm install -D @vue/tsconfig@^0.7`

### 1.2 State Management Setup
- [ ] Install Pinia: `npm install pinia@^2.3`
- [ ] Install Pinia persistence: `npm install pinia-plugin-persistedstate@^4.1`
- [ ] Create Pinia configuration file
- [ ] Set up Pinia devtools integration

### 1.3 Routing Setup
- [ ] Install Vue Router: `npm install vue-router@^4.5`
- [ ] Create router configuration file
- [ ] Define initial routes structure
- [ ] Set up route guards framework

### 1.4 Testing Infrastructure
- [ ] Install Vue Test Utils: `npm install -D @vue/test-utils@^2.4`
- [ ] Install Testing Library Vue: `npm install -D @testing-library/vue@^8.1`
- [ ] Install vitest-dom: `npm install -D vitest-dom@^0.2`
- [ ] Update `vitest.config.ts` for Vue components
- [ ] Create Vue test helpers and utilities
- [ ] Write first Vue component test as proof of concept

### 1.5 Mapbox Vue Integration
- [ ] Install vue-mapbox-gl: `npm install @studiometa/vue-mapbox-gl@^3.5`
- [ ] Create Mapbox configuration wrapper
- [ ] Test basic map initialization with Vue
- [ ] Document any API differences or limitations

### 1.6 Build Configuration
- [ ] Update `vite.config.ts` with Vue plugin
- [ ] Configure path aliases (@/ for src/)
- [ ] Set up multi-page app support for gradual migration
- [ ] Configure environment variables for Vue
- [ ] Test build process with Vue components

### 1.7 TypeScript Configuration
- [ ] Update `tsconfig.json` for Vue support
- [ ] Configure JSX/TSX for Vue
- [ ] Set up Vue component type checking
- [ ] Configure path mappings
- [ ] Test TypeScript compilation

### 1.8 Project Structure Setup
- [ ] Create `src/vue/` directory structure
- [ ] Create `src/vue/components/` subdirectories
- [ ] Create `src/vue/composables/` directory
- [ ] Create `src/vue/stores/` directory
- [ ] Create `src/vue/pages/` directory
- [ ] Create `src/vue/router/` directory
- [ ] Create `src/vue/utils/` directory
- [ ] Create `src/vue/types/` directory

### 1.9 Base Components Creation
- [ ] Create `App.vue` root component
- [ ] Create `AppHeader.vue` component
- [ ] Create `Navigation.vue` component
- [ ] Create `LoadingSpinner.vue` component
- [ ] Create `ErrorBoundary.vue` component
- [ ] Create `BaseLayout.vue` component

### 1.10 Development Environment
- [ ] Set up Vue Devtools
- [ ] Configure hot module replacement
- [ ] Set up development proxy for API
- [ ] Create development helper scripts
- [ ] Document development workflow

## Phase 2: State Management Migration (Week 2-3)

### 2.1 Occupation Store
- [ ] Create `stores/occupation.ts`
- [ ] Migrate occupation data state
- [ ] Migrate occupation cache logic
- [ ] Implement fetch actions
- [ ] Implement search functionality
- [ ] Implement filter actions
- [ ] Add error handling
- [ ] Add loading states
- [ ] Write store tests
- [ ] Integrate with persistence

### 2.2 School of Study Store
- [ ] Create `stores/schoolOfStudy.ts`
- [ ] Migrate school data state
- [ ] Migrate cache management
- [ ] Implement fetch actions
- [ ] Implement filter logic
- [ ] Add pagination support
- [ ] Add error handling
- [ ] Add loading states
- [ ] Write store tests
- [ ] Integrate with persistence

### 2.3 UI Store
- [ ] Create `stores/ui.ts`
- [ ] Migrate modal states
- [ ] Migrate notification system
- [ ] Migrate loading indicators
- [ ] Migrate error states
- [ ] Implement toast notifications
- [ ] Implement modal management
- [ ] Add keyboard shortcuts support
- [ ] Write store tests

### 2.4 Map Store
- [ ] Create `stores/map.ts`
- [ ] Define map instance state
- [ ] Implement layer management
- [ ] Implement source management
- [ ] Add interaction states
- [ ] Add popup management
- [ ] Add drawing tools state
- [ ] Implement export functionality
- [ ] Write store tests

### 2.5 API Composables
- [ ] Create `composables/useApi.ts` base composable
- [ ] Create `composables/useOccupationApi.ts`
- [ ] Create `composables/useSchoolOfStudyApi.ts`
- [ ] Create `composables/useWageApi.ts`
- [ ] Create `composables/useTravelTimeApi.ts`
- [ ] Implement request cancellation
- [ ] Implement retry logic
- [ ] Add request caching
- [ ] Write composable tests

### 2.6 Cache Migration
- [ ] Analyze current localStorage usage
- [ ] Create migration script for existing cache
- [ ] Implement backward compatibility layer
- [ ] Test cache migration with real data
- [ ] Document cache structure changes

## Phase 3: Component Migration (Week 3-5)

### 3.1 Form Components
- [ ] Create `OccupationSelect.vue`
  - [ ] Integrate Select2 functionality
  - [ ] Connect to occupation store
  - [ ] Add search functionality
  - [ ] Write component tests
- [ ] Create `SchoolOfStudySelect.vue`
  - [ ] Integrate Select2 functionality
  - [ ] Connect to school store
  - [ ] Add filter options
  - [ ] Write component tests
- [ ] Create `SearchForm.vue`
  - [ ] Build form layout
  - [ ] Add validation
  - [ ] Connect to stores
  - [ ] Write component tests
- [ ] Create `FilterControls.vue`
  - [ ] Build filter UI
  - [ ] Connect to stores
  - [ ] Add reset functionality
  - [ ] Write component tests

### 3.2 Display Components
- [ ] Create `DataTable.vue`
  - [ ] Build table structure
  - [ ] Add sorting
  - [ ] Add pagination
  - [ ] Write component tests
- [ ] Create `Legend.vue`
  - [ ] Build legend UI
  - [ ] Make interactive
  - [ ] Add color scales
  - [ ] Write component tests
- [ ] Create `PopupContent.vue`
  - [ ] Build popup template
  - [ ] Add data formatting
  - [ ] Add actions
  - [ ] Write component tests
- [ ] Create `StatsPanel.vue`
  - [ ] Build stats display
  - [ ] Connect to stores
  - [ ] Add charts
  - [ ] Write component tests

### 3.3 Map Components
- [ ] Create `MapContainer.vue`
  - [ ] Initialize Mapbox instance
  - [ ] Set up event handlers
  - [ ] Add resize handling
  - [ ] Write component tests
- [ ] Create `MapControls.vue`
  - [ ] Build control UI
  - [ ] Add zoom controls
  - [ ] Add layer toggles
  - [ ] Write component tests
- [ ] Create `OccupationMap.vue`
  - [ ] Migrate occupation visualization
  - [ ] Connect to occupation store
  - [ ] Add interactions
  - [ ] Write component tests
- [ ] Create `TravelTimeMap.vue`
  - [ ] Migrate travel time visualization
  - [ ] Add isochrone rendering
  - [ ] Add time controls
  - [ ] Write component tests
- [ ] Create `WageMap.vue`
  - [ ] Migrate wage visualization
  - [ ] Add wage scales
  - [ ] Add filtering
  - [ ] Write component tests

### 3.4 Map Composables
- [ ] Create `composables/useMapbox.ts`
  - [ ] Map initialization logic
  - [ ] Event handling setup
  - [ ] Cleanup logic
  - [ ] Write tests
- [ ] Create `composables/useMapLayers.ts`
  - [ ] Layer management
  - [ ] Style updates
  - [ ] Visibility control
  - [ ] Write tests
- [ ] Create `composables/useMapInteractions.ts`
  - [ ] Click handlers
  - [ ] Hover effects
  - [ ] Popup management
  - [ ] Write tests
- [ ] Create `composables/useMapData.ts`
  - [ ] Data loading
  - [ ] Source updates
  - [ ] Data filtering
  - [ ] Write tests
- [ ] Create `composables/useMapExport.ts`
  - [ ] Export functionality
  - [ ] Print support
  - [ ] Data download
  - [ ] Write tests

### 3.5 Page Components
- [ ] Create `pages/OccupationPage.vue`
  - [ ] Build page layout
  - [ ] Integrate components
  - [ ] Add data fetching
  - [ ] Write tests
- [ ] Create `pages/SchoolOfStudyPage.vue`
  - [ ] Build page layout
  - [ ] Integrate components
  - [ ] Add data fetching
  - [ ] Write tests
- [ ] Create `pages/WagePage.vue`
  - [ ] Build page layout
  - [ ] Integrate components
  - [ ] Add data fetching
  - [ ] Write tests
- [ ] Create `pages/TravelTimePage.vue`
  - [ ] Build page layout
  - [ ] Integrate components
  - [ ] Add data fetching
  - [ ] Write tests
- [ ] Create `pages/HomePage.vue`
  - [ ] Build landing page
  - [ ] Add navigation
  - [ ] Add overview
  - [ ] Write tests

### 3.6 Utility Components
- [ ] Create `NotificationToast.vue`
- [ ] Create `ConfirmDialog.vue`
- [ ] Create `ProgressBar.vue`
- [ ] Create `EmptyState.vue`
- [ ] Create `ErrorMessage.vue`

## Phase 4: Integration & Cleanup (Week 5-6)

### 4.1 Router Implementation
- [ ] Configure all routes
- [ ] Add route transitions
- [ ] Implement navigation guards
- [ ] Add breadcrumbs
- [ ] Set up deep linking
- [ ] Add 404 page
- [ ] Test all navigation paths

### 4.2 HTML File Updates
- [ ] Update `index.html` for Vue
- [ ] Update `access_occupation.html`
- [ ] Update `access_school_of_study.html`
- [ ] Update `access_wagelvl.html`
- [ ] Update `travel_time.html`
- [ ] Add Vue mount points
- [ ] Update script tags

### 4.3 Migration Completion
- [ ] Remove `controllers/BaseMapController.ts`
- [ ] Remove `controllers/TravelTimeMapController.ts`
- [ ] Remove individual controller files
- [ ] Remove old service files (keep as needed)
- [ ] Remove jQuery dependencies
- [ ] Remove Bootstrap JavaScript (keep CSS if needed)
- [ ] Remove Select2 direct usage
- [ ] Clean up unused imports
- [ ] Delete deprecated files

### 4.4 Testing Migration
- [ ] Migrate `baseMapController.test.ts`
- [ ] Migrate `travelTimeMapController.test.ts`
- [ ] Migrate `occupationMapController.test.ts`
- [ ] Migrate `wageMapController.test.ts`
- [ ] Migrate service tests to store tests
- [ ] Update test fixtures for Vue
- [ ] Ensure 70% coverage maintained
- [ ] Add missing component tests
- [ ] Run full regression test suite

### 4.5 Performance Optimization
- [ ] Implement route lazy loading
- [ ] Add component code splitting
- [ ] Optimize bundle with tree shaking
- [ ] Implement virtual scrolling where needed
- [ ] Add performance monitoring
- [ ] Optimize image loading
- [ ] Implement service worker for caching
- [ ] Measure and document performance metrics

### 4.6 Documentation
- [ ] Update README.md with Vue instructions
- [ ] Document component architecture
- [ ] Create component storybook (optional)
- [ ] Document store patterns
- [ ] Update API documentation
- [ ] Create migration guide
- [ ] Document deployment changes
- [ ] Add inline code documentation

### 4.7 Build & Deployment
- [ ] Update build scripts for Vue
- [ ] Test production build
- [ ] Update CI/CD pipeline
- [ ] Test deployment process
- [ ] Update environment configurations
- [ ] Verify all endpoints work
- [ ] Test on multiple browsers
- [ ] Test on mobile devices

### 4.8 Quality Assurance
- [ ] Run accessibility audit
- [ ] Fix any a11y issues
- [ ] Run performance audit
- [ ] Fix performance issues
- [ ] Security audit
- [ ] Fix security issues
- [ ] Cross-browser testing
- [ ] Mobile responsiveness testing

## Post-Migration Tasks
- [ ] Remove migration branch protection
- [ ] Archive old code (if needed)
- [ ] Update project documentation
- [ ] Team knowledge transfer session
- [ ] Create Vue best practices guide
- [ ] Set up code review guidelines
- [ ] Plan future enhancements
- [ ] Celebrate successful migration! 🎉

## Success Criteria Checklist
- [ ] All pages load without errors
- [ ] All map functionality works
- [ ] All forms and interactions work
- [ ] Test coverage ≥ 70%
- [ ] No console errors in production
- [ ] Performance metrics maintained or improved
- [ ] Bundle size increase < 150KB
- [ ] All existing features preserved
- [ ] Zero breaking changes for users
- [ ] Documentation complete and accurate

## Risk Tracking
- [ ] Monitor bundle size weekly
- [ ] Track test coverage daily
- [ ] Check for console errors after each phase
- [ ] Performance testing after each phase
- [ ] User acceptance testing per phase
- [ ] Rollback plan documented and tested

## Notes Section
Track issues encountered, decisions made, technical debt, and future improvements here.

### Issues Encountered
-

### Decisions Made
-

### Technical Debt
-

### Future Improvements
-

---

Last Updated: 2025-08-11
