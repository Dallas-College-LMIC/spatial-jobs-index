import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import StatsPanel from '../StatsPanel.vue';

describe('StatsPanel', () => {
  it('renders title', () => {
    const wrapper = mount(StatsPanel, {
      props: {
        title: 'Statistics Overview',
        stats: [],
      },
    });

    expect(wrapper.find('[data-testid="stats-title"]').text()).toBe('Statistics Overview');
  });

  it('renders statistics items', () => {
    const stats = [
      { label: 'Total Jobs', value: '25,000', icon: '💼' },
      { label: 'Average Wage', value: '$65,000', icon: '💰' },
      { label: 'Growth Rate', value: '+15%', icon: '📈' },
    ];

    const wrapper = mount(StatsPanel, {
      props: {
        title: 'Overview',
        stats,
      },
    });

    const statItems = wrapper.findAll('[data-testid="stat-item"]');
    expect(statItems).toHaveLength(3);

    expect(statItems[0]?.find('[data-testid="stat-label"]').text()).toBe('Total Jobs');
    expect(statItems[0]?.find('[data-testid="stat-value"]').text()).toBe('25,000');
    expect(statItems[0]?.find('[data-testid="stat-icon"]').text()).toBe('💼');
  });

  it('handles empty stats array', () => {
    const wrapper = mount(StatsPanel, {
      props: {
        title: 'No Stats',
        stats: [],
      },
    });

    expect(wrapper.find('[data-testid="stats-title"]').text()).toBe('No Stats');
    expect(wrapper.findAll('[data-testid="stat-item"]')).toHaveLength(0);
  });
});
