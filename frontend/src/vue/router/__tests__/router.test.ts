import { describe, it, expect } from 'vitest';
import { createRouter } from '../index';

describe('Router', () => {
  it('should have home route', () => {
    const router = createRouter();
    const route = router.getRoutes().find((r) => r.name === 'Home');

    expect(route).toBeDefined();
    expect(route?.path).toBe('/');
  });

  it('should have occupation route', () => {
    const router = createRouter();
    const route = router.getRoutes().find((r) => r.name === 'Occupation');

    expect(route).toBeDefined();
    expect(route?.path).toBe('/occupation');
  });
});
