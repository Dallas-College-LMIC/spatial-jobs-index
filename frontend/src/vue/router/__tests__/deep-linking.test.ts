import { describe, it, expect } from 'vitest';
import { createRouter } from '../index';

describe('Deep Linking Support', () => {
  it('supports direct navigation to occupation route with query params', async () => {
    const router = createRouter();
    await router.push('/occupation?id=11-2021.00');
    await router.isReady();

    expect(router.currentRoute.value.path).toBe('/occupation');
    expect(router.currentRoute.value.query).toEqual({ id: '11-2021.00' });
  });

  it('supports navigation to school of study with multiple query params', async () => {
    const router = createRouter();
    await router.push('/school-of-study?field=14&level=bachelor');
    await router.isReady();

    expect(router.currentRoute.value.path).toBe('/school-of-study');
    expect(router.currentRoute.value.query).toEqual({
      field: '14',
      level: 'bachelor',
    });
  });

  it('supports hash navigation for page sections', async () => {
    const router = createRouter();
    await router.push('/occupation#results');
    await router.isReady();

    expect(router.currentRoute.value.path).toBe('/occupation');
    expect(router.currentRoute.value.hash).toBe('#results');
  });

  it('supports combined query params and hash navigation', async () => {
    const router = createRouter();
    await router.push('/occupation?id=11-2021.00#map');
    await router.isReady();

    expect(router.currentRoute.value.path).toBe('/occupation');
    expect(router.currentRoute.value.query).toEqual({ id: '11-2021.00' });
    expect(router.currentRoute.value.hash).toBe('#map');
  });
});
