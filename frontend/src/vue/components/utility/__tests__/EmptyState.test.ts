import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import EmptyState from '../EmptyState.vue';

describe('EmptyState', () => {
  it('displays empty state message', () => {
    const wrapper = mount(EmptyState, {
      props: {
        message: 'No data available',
      },
    });

    expect(wrapper.text()).toContain('No data available');
  });

  it('has empty state styling class', () => {
    const wrapper = mount(EmptyState, {
      props: {
        message: 'No data',
      },
    });

    expect(wrapper.classes()).toContain('empty-state');
  });
});
