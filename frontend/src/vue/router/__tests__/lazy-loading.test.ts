import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createRouter } from '../index';

describe('Router Lazy Loading', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should lazy load occupation route component', () => {
    const router = createRouter();
    const routes = router.getRoutes();

    const occupationRoute = routes.find((r) => r.name === 'Occupation');

    // Lazy-loaded components should be functions (dynamic imports)
    expect(occupationRoute?.components?.default).toBeDefined();
    expect(typeof occupationRoute?.components?.default).toBe('function');
  });

  it('should lazy load all non-critical route components', () => {
    const router = createRouter();
    const routes = router.getRoutes();

    const lazyRoutes = ['SchoolOfStudy', 'WageLevel', 'TravelTime'];

    lazyRoutes.forEach((routeName) => {
      const route = routes.find((r) => r.name === routeName);
      expect(route).toBeDefined();
      expect(typeof route?.components?.default).toBe('function');
    });
  });

  it('should eagerly load critical routes for better initial performance', () => {
    const router = createRouter();
    const routes = router.getRoutes();

    // Home and NotFound pages should be eagerly loaded
    const homeRoute = routes.find((r) => r.name === 'Home');
    const notFoundRoute = routes.find((r) => r.name === 'NotFound');

    // Eagerly loaded components are objects, not functions
    expect(homeRoute).toBeDefined();
    expect(typeof homeRoute?.components?.default).toBe('object');

    expect(notFoundRoute).toBeDefined();
    expect(typeof notFoundRoute?.components?.default).toBe('object');
  });
});
