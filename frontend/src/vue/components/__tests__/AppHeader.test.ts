import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import { createMemoryHistory, createRouter } from 'vue-router';
import AppHeader from '../AppHeader.vue';

describe('AppHeader', () => {
  const createTestRouter = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/wage', component: { template: '<div>Wage</div>' } },
        { path: '/occupation', component: { template: '<div>Occupation</div>' } },
        { path: '/school-of-study', component: { template: '<div>School</div>' } },
        { path: '/travel-time', component: { template: '<div>Travel</div>' } },
      ],
    });
  };

  it('renders a navbar element', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
      },
    });

    expect(wrapper.find('nav.navbar').exists()).toBe(true);
  });

  it('renders navigation text', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.text()).toContain('Project Home');
    expect(wrapper.text()).toContain('Job Access by Wage Level');
  });

  it('has correct classes', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.find('nav.navbar#banner').exists()).toBe(true);
  });

  it('renders Dallas College logo', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
      },
    });

    const logo = wrapper.find('img#dc_logo');
    expect(logo.exists()).toBe(true);
    expect(logo.attributes('alt')).toBe('Dallas College Logo');
  });

  it('renders Project Home navigation link', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
      },
    });

    const homeLink = wrapper
      .findAllComponents({ name: 'RouterLink' })
      .find((link) => link.text() === 'Project Home');
    expect(homeLink).toBeDefined();
    expect(homeLink?.props('to')).toBe('/');
  });
});
