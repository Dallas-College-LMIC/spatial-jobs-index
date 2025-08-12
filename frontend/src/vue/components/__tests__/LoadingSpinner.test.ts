import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import LoadingSpinner from '../LoadingSpinner.vue';

describe('LoadingSpinner', () => {
  it('renders a spinner', () => {
    const wrapper = mount(LoadingSpinner);
    expect(wrapper.find('.spinner').exists()).toBe(true);
  });

  it('shows default loading text', () => {
    const wrapper = mount(LoadingSpinner);
    expect(wrapper.text()).toContain('Loading...');
  });
});
