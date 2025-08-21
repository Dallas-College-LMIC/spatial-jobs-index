import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import HomePage from '../HomePage.vue';

describe('HomePage', () => {
  it('should render homepage heading', () => {
    const wrapper = mount(HomePage);

    expect(wrapper.find('h1').text()).toBe('Spatial Jobs Index');
  });

  it('should render welcome message', () => {
    const wrapper = mount(HomePage);

    expect(wrapper.find('.welcome-message').exists()).toBe(true);
    expect(wrapper.find('.welcome-message').text()).toContain('Explore job accessibility');
  });
});
