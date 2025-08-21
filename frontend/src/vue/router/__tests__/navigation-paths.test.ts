import { describe, it, expect } from 'vitest';
import { createRouter } from '../index';

describe('Navigation Paths', () => {
  it('navigates to home page', async () => {
    const router = createRouter();
    await router.push('/');
    await router.isReady();

    expect(router.currentRoute.value.name).toBe('Home');
    expect(router.currentRoute.value.path).toBe('/');
  });

  it('navigates to occupation page', async () => {
    const router = createRouter();
    await router.push('/occupation');
    await router.isReady();

    expect(router.currentRoute.value.name).toBe('Occupation');
    expect(router.currentRoute.value.path).toBe('/occupation');
  });

  it('navigates to school of study page', async () => {
    const router = createRouter();
    await router.push('/school-of-study');
    await router.isReady();

    expect(router.currentRoute.value.name).toBe('SchoolOfStudy');
    expect(router.currentRoute.value.path).toBe('/school-of-study');
  });

  it('handles 404 for unknown routes', async () => {
    const router = createRouter();
    await router.push('/unknown-route');
    await router.isReady();

    expect(router.currentRoute.value.name).toBe('NotFound');
    expect(router.currentRoute.value.path).toBe('/unknown-route');
  });
});
