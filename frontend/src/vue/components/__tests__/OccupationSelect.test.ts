import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { setActivePinia, createPinia } from 'pinia';
import OccupationSelect from '../OccupationSelect.vue';
import { useOccupationStore } from '../../stores/occupation';

describe('OccupationSelect', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('renders select element', () => {
    const wrapper = mount(OccupationSelect);
    expect(wrapper.find('select').exists()).toBe(true);
  });

  it('displays placeholder when no occupation selected', () => {
    const wrapper = mount(OccupationSelect);
    const placeholder = wrapper.find('option[value=""]');
    expect(placeholder.exists()).toBe(true);
    expect(placeholder.text()).toBe('Select an occupation...');
  });

  it('loads occupation IDs on mount', async () => {
    const store = useOccupationStore();
    const fetchSpy = vi.spyOn(store, 'fetchOccupationIds');

    mount(OccupationSelect);

    expect(fetchSpy).toHaveBeenCalled();
  });

  it('displays occupation options from store', async () => {
    const store = useOccupationStore();
    store.occupations = [
      { code: 'occ1', name: 'Software Developer' },
      { code: 'occ2', name: 'Data Scientist' },
    ];

    const wrapper = mount(OccupationSelect);
    await wrapper.vm.$nextTick();

    const options = wrapper.findAll('option');
    expect(options).toHaveLength(3); // placeholder + 2 occupations
    expect(options[1]?.attributes('value')).toBe('occ1');
    expect(options[1]?.text()).toBe('Software Developer');
  });

  it('emits update event when handleChange is called', async () => {
    const store = useOccupationStore();
    store.occupations = [{ code: 'occ1', name: 'Software Developer' }];

    const wrapper = mount(OccupationSelect);
    await wrapper.vm.$nextTick();

    // Create a mock event
    const mockEvent = {
      target: {
        value: 'occ1',
      },
    } as unknown as Event;

    // Call handleChange directly through the component instance
    // @ts-ignore - accessing private method for testing
    wrapper.vm.handleChange(mockEvent);

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['occ1']);
  });

  it('updates store when handleChange is called', async () => {
    const store = useOccupationStore();
    store.occupations = [{ code: 'occ1', name: 'Software Developer' }];

    const wrapper = mount(OccupationSelect);
    await wrapper.vm.$nextTick();

    // Create a mock event
    const mockEvent = {
      target: {
        value: 'occ1',
      },
    } as unknown as Event;

    // Call handleChange directly through the component instance
    // @ts-ignore - accessing exposed method for testing
    wrapper.vm.handleChange(mockEvent);

    expect(store.selectedOccupationId).toBe('occ1');
  });

  it('shows loading state while fetching', async () => {
    const store = useOccupationStore();
    store.isLoading = true;

    const wrapper = mount(OccupationSelect);

    expect(wrapper.find('select').attributes('disabled')).toBeDefined();
    expect(wrapper.find('.loading-indicator').exists()).toBe(true);
  });
});
