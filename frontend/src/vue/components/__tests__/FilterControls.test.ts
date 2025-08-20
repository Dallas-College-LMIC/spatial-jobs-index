import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import FilterControls from '../FilterControls.vue';
import { useOccupationStore } from '../../stores/occupation';

describe('FilterControls', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('renders filter controls container', () => {
    const wrapper = mount(FilterControls);
    expect(wrapper.find('.filter-controls').exists()).toBe(true);
  });

  it('renders wage level filter', () => {
    const wrapper = mount(FilterControls);
    const wageFilter = wrapper.find('.wage-filter');
    expect(wageFilter.exists()).toBe(true);
    expect(wageFilter.find('label').text()).toContain('Wage Level');
  });

  it('renders education level filter', () => {
    const wrapper = mount(FilterControls);
    const educationFilter = wrapper.find('.education-filter');
    expect(educationFilter.exists()).toBe(true);
    expect(educationFilter.find('label').text()).toContain('Education Level');
  });

  it('renders reset button', () => {
    const wrapper = mount(FilterControls);
    const resetButton = wrapper.find('button.reset-button');
    expect(resetButton.exists()).toBe(true);
    expect(resetButton.text()).toBe('Reset Filters');
  });

  it('emits filter-change event when wage filter changes', async () => {
    const wrapper = mount(FilterControls);
    const wageSelect = wrapper.find('.wage-filter select');

    await wageSelect.setValue('high');

    expect(wrapper.emitted('filter-change')).toBeTruthy();
    expect(wrapper.emitted('filter-change')![0]).toEqual([
      {
        wageLevel: 'high',
        educationLevel: 'all',
      },
    ]);
  });

  it('emits filter-change event when education filter changes', async () => {
    const wrapper = mount(FilterControls);
    const educationSelect = wrapper.find('.education-filter select');

    await educationSelect.setValue('bachelors');

    expect(wrapper.emitted('filter-change')).toBeTruthy();
    expect(wrapper.emitted('filter-change')![0]).toEqual([
      {
        wageLevel: 'all',
        educationLevel: 'bachelors',
      },
    ]);
  });

  it('updates store when filters change', async () => {
    const wrapper = mount(FilterControls);
    const store = useOccupationStore();
    const setFilterSpy = vi.spyOn(store, 'setFilterOptions');

    const wageSelect = wrapper.find('.wage-filter select');
    await wageSelect.setValue('high');

    expect(setFilterSpy).toHaveBeenCalledWith({
      wageLevel: 'high',
      educationLevel: 'all',
    });
  });

  it('resets all filters when reset button is clicked', async () => {
    const wrapper = mount(FilterControls);

    // Set some filters first
    const wageSelect = wrapper.find('.wage-filter select');
    const educationSelect = wrapper.find('.education-filter select');
    await wageSelect.setValue('high');
    await educationSelect.setValue('bachelors');

    // Click reset
    const resetButton = wrapper.find('button.reset-button');
    await resetButton.trigger('click');

    // Check that filters are reset
    expect((wageSelect.element as HTMLSelectElement).value).toBe('all');
    expect((educationSelect.element as HTMLSelectElement).value).toBe('all');

    // Check that reset event was emitted
    expect(wrapper.emitted('filter-reset')).toBeTruthy();
  });

  it('emits filter-change event with all filters reset', async () => {
    const wrapper = mount(FilterControls);

    // Set some filters
    const wageSelect = wrapper.find('.wage-filter select');
    await wageSelect.setValue('high');

    // Reset
    const resetButton = wrapper.find('button.reset-button');
    await resetButton.trigger('click');

    // Check the last filter-change event
    const filterChangeEvents = wrapper.emitted('filter-change');
    const lastEvent = filterChangeEvents![filterChangeEvents!.length - 1];
    expect(lastEvent).toEqual([
      {
        wageLevel: 'all',
        educationLevel: 'all',
      },
    ]);
  });

  it('shows active filter count', async () => {
    const wrapper = mount(FilterControls);

    // Initially no active filters
    expect(wrapper.find('.filter-count').exists()).toBe(false);

    // Set a filter
    const wageSelect = wrapper.find('.wage-filter select');
    await wageSelect.setValue('high');

    // Should show count
    const filterCount = wrapper.find('.filter-count');
    expect(filterCount.exists()).toBe(true);
    expect(filterCount.text()).toBe('1 active filter');

    // Set another filter
    const educationSelect = wrapper.find('.education-filter select');
    await educationSelect.setValue('bachelors');

    // Should show plural
    expect(wrapper.find('.filter-count').text()).toBe('2 active filters');
  });

  it('disables reset button when no filters are active', () => {
    const wrapper = mount(FilterControls);
    const resetButton = wrapper.find('button.reset-button');

    expect(resetButton.attributes('disabled')).toBeDefined();
  });

  it('enables reset button when filters are active', async () => {
    const wrapper = mount(FilterControls);
    const resetButton = wrapper.find('button.reset-button');

    // Set a filter
    const wageSelect = wrapper.find('.wage-filter select');
    await wageSelect.setValue('high');

    expect(resetButton.attributes('disabled')).toBeUndefined();
  });
});
