import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createMemoryHistory, createRouter } from 'vue-router';
import axe from 'axe-core';
import AppHeader from '../../components/AppHeader.vue';

describe('Accessibility Tests', () => {
  beforeEach(() => {
    // Clean up document body before each test
    document.body.innerHTML = '';
  });

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

  async function checkAccessibility(wrapper: any) {
    document.body.appendChild(wrapper.element);
    const results = await axe.run(wrapper.element);
    return results.violations;
  }

  it('AppHeader should have no accessibility violations', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
      },
    });

    const violations = await checkAccessibility(wrapper);
    expect(violations).toHaveLength(0);
  });
});
