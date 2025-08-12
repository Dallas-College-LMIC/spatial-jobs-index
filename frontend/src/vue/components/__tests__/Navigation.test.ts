import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import Navigation from '../Navigation.vue';

describe('Navigation', () => {
  it('renders navigation links', () => {
    const wrapper = mount(Navigation);
    expect(wrapper.text()).toContain('Occupation');
  });

  it('renders multiple navigation items', () => {
    const wrapper = mount(Navigation);
    expect(wrapper.text()).toContain('School of Study');
    expect(wrapper.text()).toContain('Wage Level');
    expect(wrapper.text()).toContain('Travel Time');
  });
});
