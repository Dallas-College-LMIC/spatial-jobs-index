import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import App from '../../components/App.vue';

describe('App Component', () => {
  it('should mount successfully', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('should render RouterView for navigation', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    expect(wrapper.findComponent({ name: 'RouterView' }).exists()).toBe(true);
  });

  it('should have transition wrapper for route changes', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    const transition = wrapper.findComponent({ name: 'Transition' });
    expect(transition.exists()).toBe(true);
  });

  it('should configure transition with fade-slide animation', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    const transition = wrapper.findComponent({ name: 'Transition' });
    expect(transition.props('name')).toBe('fade-slide');
    expect(transition.props('mode')).toBe('out-in');
  });

  it('should have transition styles defined', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    // Check that component has styles
    const component = wrapper.vm.$options;
    expect(component.__scopeId).toBeDefined();
  });
});
