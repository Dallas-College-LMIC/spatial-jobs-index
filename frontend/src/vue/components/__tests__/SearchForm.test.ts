import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import SearchForm from '../SearchForm.vue';
import { useOccupationStore } from '../../stores/occupation';
import OccupationSelect from '../OccupationSelect.vue';
import SchoolOfStudySelect from '../SchoolOfStudySelect.vue';

describe('SearchForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('renders search input field', () => {
    const wrapper = mount(SearchForm);
    const input = wrapper.find('input[type="text"]');
    expect(input.exists()).toBe(true);
    expect(input.attributes('placeholder')).toBe('Search...');
  });

  it('renders occupation select component', () => {
    const wrapper = mount(SearchForm);
    const occupationSelect = wrapper.findComponent(OccupationSelect);
    expect(occupationSelect.exists()).toBe(true);
  });

  it('renders school of study select component', () => {
    const wrapper = mount(SearchForm);
    const schoolSelect = wrapper.findComponent(SchoolOfStudySelect);
    expect(schoolSelect.exists()).toBe(true);
  });

  it('renders search button', () => {
    const wrapper = mount(SearchForm);
    const button = wrapper.find('button[type="submit"]');
    expect(button.exists()).toBe(true);
    expect(button.text()).toBe('Search');
  });

  it('updates search query in occupation store when typing', async () => {
    const wrapper = mount(SearchForm);
    const store = useOccupationStore();

    // Spy on the store method
    const setSearchQuerySpy = vi.spyOn(store, 'setSearchQuery');

    const input = wrapper.find('input[type="text"]');
    await input.setValue('test query');

    expect(setSearchQuerySpy).toHaveBeenCalledWith('test query');
  });

  it('emits search event when form is submitted with valid data', async () => {
    const wrapper = mount(SearchForm);

    // Set some valid data
    const input = wrapper.find('input[type="text"]');
    await input.setValue('test search');

    const form = wrapper.find('form');
    await form.trigger('submit.prevent');

    expect(wrapper.emitted('search')).toBeTruthy();
    expect(wrapper.emitted('search')![0]).toEqual([
      {
        searchQuery: 'test search',
        occupationId: '',
        schoolId: '',
      },
    ]);
  });

  it('emits search event with form data when submitted', async () => {
    const wrapper = mount(SearchForm, {
      global: {
        stubs: {
          OccupationSelect: {
            template:
              '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><option value="">Select...</option><option value="OCC123">Test</option></select>',
            props: ['modelValue'],
            emits: ['update:modelValue'],
          },
          SchoolOfStudySelect: {
            template:
              '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><option value="">Select...</option><option value="SCH456">Test</option></select>',
            props: ['modelValue'],
            emits: ['update:modelValue'],
          },
        },
      },
    });

    const input = wrapper.find('input[type="text"]');
    await input.setValue('test search');

    // Update the occupation select by changing its value
    const occupationSelect = wrapper.find('select').element as HTMLSelectElement;
    occupationSelect.value = 'OCC123';
    await wrapper.find('select').trigger('change');

    // Update the school select by changing its value
    const allSelects = wrapper.findAll('select');
    if (allSelects.length > 1 && allSelects[1]) {
      const schoolSelect = allSelects[1].element as HTMLSelectElement;
      schoolSelect.value = 'SCH456';
      await allSelects[1].trigger('change');
    }

    await wrapper.vm.$nextTick();

    const form = wrapper.find('form');
    await form.trigger('submit.prevent');

    expect(wrapper.emitted('search')).toBeTruthy();
    expect(wrapper.emitted('search')![0]).toEqual([
      {
        searchQuery: 'test search',
        occupationId: 'OCC123',
        schoolId: 'SCH456',
      },
    ]);
  });

  it('validates form before submission', async () => {
    const wrapper = mount(SearchForm);
    const form = wrapper.find('form');

    // Try to submit empty form
    await form.trigger('submit.prevent');

    // Should show validation error
    const error = wrapper.find('.validation-error');
    expect(error.exists()).toBe(true);
    expect(error.text()).toContain('Please select an occupation or school of study');
  });

  it('clears validation error when input is provided', async () => {
    const wrapper = mount(SearchForm, {
      global: {
        stubs: {
          OccupationSelect: {
            template:
              '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><option value="">Select...</option><option value="OCC123">Test</option></select>',
            props: ['modelValue'],
            emits: ['update:modelValue'],
          },
          SchoolOfStudySelect: true,
        },
      },
    });

    const form = wrapper.find('form');

    // Submit empty form to trigger validation
    await form.trigger('submit.prevent');
    expect(wrapper.find('.validation-error').exists()).toBe(true);

    // Select an occupation by changing select value
    const occupationSelect = wrapper.find('select').element as HTMLSelectElement;
    occupationSelect.value = 'OCC123';
    await wrapper.find('select').trigger('change');
    await wrapper.vm.$nextTick();

    // Validation error should be cleared
    expect(wrapper.find('.validation-error').exists()).toBe(false);
  });

  it('shows loading state when search is in progress', async () => {
    const wrapper = mount(SearchForm, {
      props: {
        isLoading: true,
      },
    });

    const button = wrapper.find('button[type="submit"]');
    expect(button.attributes('disabled')).toBeDefined();
    expect(button.text()).toBe('Searching...');
  });
});
