import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import Breadcrumbs from '../Breadcrumbs.vue';

describe('Breadcrumbs', () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          name: 'Home',
          component: { template: '<div></div>' },
          meta: { breadcrumb: 'Home' },
        },
        {
          path: '/occupation',
          name: 'Occupation',
          component: { template: '<div></div>' },
          meta: { breadcrumb: 'Occupations' },
        },
        {
          path: '/school-of-study',
          name: 'SchoolOfStudy',
          component: { template: '<div></div>' },
          meta: { breadcrumb: 'Schools' },
        },
      ],
    });
  };

  it('renders home breadcrumb for root path', async () => {
    const router = createTestRouter();
    await router.push('/');

    const wrapper = mount(Breadcrumbs, {
      global: {
        plugins: [router],
      },
    });

    const items = wrapper.findAll('.breadcrumb-item');
    expect(items).toHaveLength(1);
    expect(items[0]?.text()).toBe('Home');
  });

  it('renders multiple breadcrumbs for nested route', async () => {
    const router = createTestRouter();
    await router.push('/occupation');

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

  it('shows current page as active breadcrumb', async () => {
    const router = createTestRouter();
    await router.push('/occupation');

    const wrapper = mount(Breadcrumbs, {
      global: {
        plugins: [router],
      },
    });

    const items = wrapper.findAll('.breadcrumb-item');
    expect(items[1]?.classes()).toContain('active');
  });

  it('makes non-active breadcrumbs clickable', async () => {
    const router = createTestRouter();
    await router.push('/occupation');

    const wrapper = mount(Breadcrumbs, {
      global: {
        plugins: [router],
      },
    });

    const homeLink = wrapper.find('.breadcrumb-item a');
    expect(homeLink.exists()).toBe(true);
    expect(homeLink.attributes('href')).toBe('/');
  });

  it('separates breadcrumbs with divider', async () => {
    const router = createTestRouter();
    await router.push('/occupation');

    const wrapper = mount(Breadcrumbs, {
      global: {
        plugins: [router],
      },
    });

    const dividers = wrapper.findAll('.breadcrumb-divider');
    expect(dividers).toHaveLength(1);
  });
});
