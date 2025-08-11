import { describe, it, expect } from 'vitest';
import { createRouter } from '../../router';

describe('Router Routes', () => {
  it('should have occupation route', () => {
    const router = createRouter();
    const route = router.getRoutes().find((r) => r.name === 'Occupation');
    expect(route).toBeDefined();
    expect(route?.path).toBe('/occupation');
  });
});
