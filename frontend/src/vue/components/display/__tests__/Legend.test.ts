import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Legend from '../Legend.vue';

describe('Legend', () => {
  it('renders legend title', () => {
    const wrapper = mount(Legend, {
      props: {
        title: 'Job Accessibility',
        items: [],
      },
    });

    expect(wrapper.find('[data-testid="legend-title"]').text()).toBe('Job Accessibility');
  });

  it('renders legend items with colors', () => {
    const items = [
      { label: 'Low', color: '#fee5d9' },
      { label: 'Medium', color: '#fcae91' },
      { label: 'High', color: '#fb6a4a' },
    ];

    const wrapper = mount(Legend, {
      props: {
        title: 'Accessibility Levels',
        items,
      },
    });

    const legendItems = wrapper.findAll('[data-testid="legend-item"]');
    expect(legendItems).toHaveLength(3);

    expect(legendItems[0]?.find('[data-testid="legend-label"]').text()).toBe('Low');
    expect(legendItems[0]?.find('[data-testid="legend-color"]').attributes('style')).toContain(
      '#fee5d9'
    );
  });

  it('handles empty items array', () => {
    const wrapper = mount(Legend, {
      props: {
        title: 'Empty Legend',
        items: [],
      },
    });

    expect(wrapper.find('[data-testid="legend-title"]').text()).toBe('Empty Legend');
    expect(wrapper.findAll('[data-testid="legend-item"]')).toHaveLength(0);
  });
});
