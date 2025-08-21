import { describe, it, expect } from 'vitest';
import { createRouter } from '../../router';

describe('Router Configuration', () => {
  it('should create a router instance with routes', () => {
    const router = createRouter();
    expect(router).toBeDefined();
    expect(router.getRoutes().length).toBeGreaterThan(0);
  });

  it('should have a 404 catch-all route', () => {
    const router = createRouter();
    const routes = router.getRoutes();
    const notFoundRoute = routes.find((route) => route.name === 'NotFound');
    expect(notFoundRoute).toBeDefined();
    expect(notFoundRoute?.path).toBe('/:pathMatch(.*)*');
  });
});
