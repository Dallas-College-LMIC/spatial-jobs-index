import { describe, it, expect, beforeEach } from 'vitest';
import { createRouter } from '../index';
import { Router } from 'vue-router';

describe('Router Configuration', () => {
  let router: Router;

  beforeEach(() => {
    router = createRouter();
  });

  describe('Route Definitions', () => {
    it('should have Occupation route with OccupationPage component', () => {
      const occupationRoute = router.getRoutes().find((route) => route.name === 'Occupation');
      expect(occupationRoute).toBeDefined();
      expect(occupationRoute?.path).toBe('/occupation');
      // Check that the component exists (it's now lazy-loaded as a function)
      const component = occupationRoute?.components?.default;
      expect(component).toBeDefined();
      expect(typeof component).toBe('function'); // Lazy-loaded components are functions
    });

    it('should have SchoolOfStudy route with SchoolOfStudyPage component', () => {
      const schoolRoute = router.getRoutes().find((route) => route.name === 'SchoolOfStudy');
      expect(schoolRoute).toBeDefined();
      expect(schoolRoute?.path).toBe('/school-of-study');
      const component = schoolRoute?.components?.default;
      expect(component).toBeDefined();
      expect(typeof component).toBe('function'); // Lazy-loaded components are functions
    });

    it('should have WageLevel route configured', () => {
      const wageRoute = router.getRoutes().find((route) => route.name === 'WageLevel');
      expect(wageRoute).toBeDefined();
      expect(wageRoute?.path).toBe('/wage-level');
    });

    it('should have TravelTime route configured', () => {
      const travelRoute = router.getRoutes().find((route) => route.name === 'TravelTime');
      expect(travelRoute).toBeDefined();
      expect(travelRoute?.path).toBe('/travel-time');
    });
  });
});
