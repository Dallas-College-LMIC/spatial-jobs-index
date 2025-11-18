import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createMemoryHistory, createRouter } from 'vue-router';
import HomePage from '../HomePage.vue';

describe('HomePage', () => {
  const createTestRouter = () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: HomePage },
        { path: '/wage', component: { template: '<div>Wage</div>' } },
        { path: '/occupation', component: { template: '<div>Occupation</div>' } },
        { path: '/school-of-study', component: { template: '<div>School</div>' } },
        { path: '/travel-time', component: { template: '<div>Travel</div>' } },
      ],
    });
    return router;
  };

  it('should render homepage heading', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(HomePage, {
      global: {
        plugins: [router],
      },
    });

    expect(wrapper.find('h1').text()).toBe('Dallas-Ft. Worth Spatial Jobs Index');
  });

  it('should render welcome message', async () => {
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();

    const wrapper = mount(HomePage, {
      global: {
        plugins: [router],
      },
    });

    expect(wrapper.text()).toContain(
      'A Web-based Tool for Understanding Spatial Access to Employment'
    );
  });
});
