import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import DataTable from '../DataTable.vue';

describe('DataTable', () => {
  const mockData = [
    { id: 1, name: 'Software Developer', count: 1500, wage: 85000 },
    { id: 2, name: 'Data Analyst', count: 800, wage: 65000 },
    { id: 3, name: 'Product Manager', count: 400, wage: 95000 },
  ];

  const mockColumns = [
    { key: 'name', label: 'Occupation', sortable: true },
    { key: 'count', label: 'Job Count', sortable: true },
    { key: 'wage', label: 'Average Wage', sortable: true, format: 'currency' },
  ];

  it('should render table with headers', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const headers = wrapper.findAll('th');
    expect(headers).toHaveLength(3);
    expect(headers[0]?.text()).toBe('Occupation');
    expect(headers[1]?.text()).toBe('Job Count');
    expect(headers[2]?.text()).toBe('Average Wage');
  });

  it('should render data rows', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const rows = wrapper.findAll('tbody tr');
    expect(rows).toHaveLength(3);

    const firstRowCells = rows[0]?.findAll('td');
    expect(firstRowCells?.[0]?.text()).toBe('Software Developer');
    expect(firstRowCells?.[1]?.text()).toBe('1500');
    expect(firstRowCells?.[2]?.text()).toBe('$85,000');
  });

  it('should show empty state when no data', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: [],
        columns: mockColumns,
      },
    });

    expect(wrapper.text()).toContain('No data available');
  });

  it('should show sort indicators on sortable columns', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const sortButtons = wrapper.findAll('th button');
    expect(sortButtons).toHaveLength(3);
  });

  it('should emit sort event when clicking sortable header', async () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const firstHeader = wrapper.find('th button');
    await firstHeader.trigger('click');

    expect(wrapper.emitted('sort')).toBeTruthy();
    expect(wrapper.emitted('sort')?.[0]).toEqual([{ column: 'name', direction: 'asc' }]);
  });

  it('should show pagination controls when pageSize is set', () => {
    const largeData = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      count: (i + 1) * 100,
      wage: (i + 1) * 1000,
    }));

    const wrapper = mount(DataTable, {
      props: {
        data: largeData,
        columns: mockColumns,
        pageSize: 10,
      },
    });

    expect(wrapper.find('.pagination').exists()).toBe(true);
  });

  it('should display correct number of rows per page', () => {
    const largeData = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      count: (i + 1) * 100,
      wage: (i + 1) * 1000,
    }));

    const wrapper = mount(DataTable, {
      props: {
        data: largeData,
        columns: mockColumns,
        pageSize: 10,
      },
    });

    const rows = wrapper.findAll('tbody tr');
    expect(rows).toHaveLength(10);
  });

  it('should format currency values', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns,
      },
    });

    const wageCell = wrapper.findAll('tbody tr')[0]?.findAll('td')[2];
    expect(wageCell?.text()).toBe('$85,000');
  });
});
