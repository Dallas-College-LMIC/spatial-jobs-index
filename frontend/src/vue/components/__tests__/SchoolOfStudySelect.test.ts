import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { setActivePinia, createPinia } from 'pinia';
import SchoolOfStudySelect from '../SchoolOfStudySelect.vue';
import { useSchoolOfStudyStore } from '../../stores/schoolOfStudy';

describe('SchoolOfStudySelect', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('renders select element', () => {
    const wrapper = mount(SchoolOfStudySelect);
    expect(wrapper.find('select').exists()).toBe(true);
  });

  it('displays placeholder when no school selected', () => {
    const wrapper = mount(SchoolOfStudySelect);
    const placeholder = wrapper.find('option[value=""]');
    expect(placeholder.exists()).toBe(true);
    expect(placeholder.text()).toBe('Select a school of study...');
  });

  it('loads school IDs on mount', async () => {
    const store = useSchoolOfStudyStore();
    const fetchSpy = vi.spyOn(store, 'fetchSchoolIds');

    mount(SchoolOfStudySelect);

    expect(fetchSpy).toHaveBeenCalled();
  });
});
