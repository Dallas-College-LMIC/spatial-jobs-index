import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter } from '../index';
import Breadcrumbs from '../../components/navigation/Breadcrumbs.vue';

describe('Breadcrumbs Router Integration', () => {
  it('displays correct breadcrumb for occupation route', async () => {
    const router = createRouter();
    await router.push('/occupation');
    await router.isReady();

    const wrapper = mount(Breadcrumbs, {
      global: {
        plugins: [router],
      },
    });

    const items = wrapper.findAll('.breadcrumb-item');
    expect(items).toHaveLength(2);
    expect(items[0]?.text()).toBe('Home');
    expect(items[1]?.text()).toBe('Occupations');
  });

  it('displays correct breadcrumb for school of study route', async () => {
    const router = createRouter();
    await router.push('/school-of-study');
    await router.isReady();

    const wrapper = mount(Breadcrumbs, {
      global: {
        plugins: [router],
      },
    });

    const items = wrapper.findAll('.breadcrumb-item');
    expect(items).toHaveLength(2);
    expect(items[0]?.text()).toBe('Home');
    expect(items[1]?.text()).toBe('Schools of Study');
  });
});
