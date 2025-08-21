import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import NotFoundPage from '../NotFoundPage.vue';

describe('NotFoundPage', () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
  });

  it('renders 404 message', () => {
    const wrapper = mount(NotFoundPage, {
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.text()).toContain('404');
  });

  it('renders page not found message', () => {
    const wrapper = mount(NotFoundPage, {
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.text()).toContain('Page Not Found');
  });

  it('has a link to home page', () => {
    const wrapper = mount(NotFoundPage, {
      global: {
        plugins: [router],
      },
    });
    const link = wrapper.find('a');
    expect(link.exists()).toBe(true);
    expect(link.text()).toContain('Go to Home');
  });
});
