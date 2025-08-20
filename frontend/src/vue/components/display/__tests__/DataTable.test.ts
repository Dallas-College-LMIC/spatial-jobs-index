import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import DataTable from '../DataTable.vue';

describe('DataTable', () => {
  const mockColumns = [
    { key: 'name', label: 'Occupation', sortable: true },
    { key: 'jobs', label: 'Number of Jobs', sortable: true },
    { key: 'wage', label: 'Average Wage', sortable: true, format: 'currency' },
  ];

  it('renders empty state when no data provided', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: [],
        columns: mockColumns,
      },
    });

    expect(wrapper.find('[data-testid="empty-state"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('No data available');
  });

  it('renders table with correct headers', () => {
    const mockData = [{ id: 1, name: 'Software Developer', jobs: 1500, wage: 75000 }];

    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const headers = wrapper.findAll('th');
    expect(headers).toHaveLength(3);
    expect(headers[0]?.text()).toBe('Occupation');
    expect(headers[1]?.text()).toBe('Number of Jobs');
    expect(headers[2]?.text()).toBe('Average Wage');
  });

  it('renders table rows with data', () => {
    const mockData = [
      { id: 1, name: 'Software Developer', jobs: 1500, wage: 75000 },
      { id: 2, name: 'Data Scientist', jobs: 800, wage: 85000 },
    ];

    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const rows = wrapper.findAll('tbody tr');
    expect(rows).toHaveLength(2);

    const firstRowCells = rows[0]?.findAll('td');
    expect(firstRowCells?.[0]?.text()).toBe('Software Developer');
    expect(firstRowCells?.[1]?.text()).toBe('1500');
    expect(firstRowCells?.[2]?.text()).toBe('$75,000'); // Currency formatted
  });

  it('formats currency values correctly', () => {
    const mockData = [{ id: 1, name: 'Software Developer', jobs: 1500, wage: 75000 }];

    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const wageCell = wrapper.find('tbody tr td:nth-child(3)');
    expect(wageCell.text()).toBe('$75,000');
  });

  it('shows loading state when loading prop is true', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: [],
        columns: mockColumns,
        loading: true,
      },
    });

    expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true);
    expect(wrapper.find('table').exists()).toBe(false);
  });
});
