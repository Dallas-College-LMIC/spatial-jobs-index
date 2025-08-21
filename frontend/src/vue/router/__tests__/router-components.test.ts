import { describe, it, expect } from 'vitest';
import { createRouter } from '../index';

describe('Router Components', () => {
  it('uses WagePage component for wage-level route', async () => {
    const router = createRouter();
    await router.push('/wage-level');
    await router.isReady();

    const component = router.currentRoute.value.matched[0]?.components?.default;
    expect(component).toBeDefined();
    expect(component?.name).toBe('WagePage');
  });

  it('uses TravelTimePage component for travel-time route', async () => {
    const router = createRouter();
    await router.push('/travel-time');
    await router.isReady();

    const component = router.currentRoute.value.matched[0]?.components?.default;
    expect(component).toBeDefined();
    expect(component?.name).toBe('TravelTimePage');
  });
});
