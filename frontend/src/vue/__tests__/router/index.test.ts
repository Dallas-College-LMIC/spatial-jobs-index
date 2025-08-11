import { describe, it, expect } from 'vitest';
import { createRouter } from '../../router';

describe('Router Configuration', () => {
  it('should create a router instance with routes', () => {
    const router = createRouter();
    expect(router).toBeDefined();
    expect(router.getRoutes().length).toBeGreaterThan(0);
  });
});
