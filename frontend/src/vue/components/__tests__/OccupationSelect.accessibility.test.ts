import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import OccupationSelect from '../OccupationSelect.vue';

describe('OccupationSelect Accessibility', () => {
  it('should have an accessible label for the select element', () => {
    const wrapper = mount(OccupationSelect, {
      props: {
        modelValue: '',
      },
      global: {
        plugins: [createTestingPinia()],
      },
    });

    const select = wrapper.find('select');

    // Check for aria-label or associated label
    const hasAriaLabel = select.attributes('aria-label');
    const labelFor = wrapper.find(`label[for="${select.attributes('id')}"]`);

    const hasAccessibleLabel = Boolean(hasAriaLabel) || labelFor.exists();
    expect(hasAccessibleLabel).toBe(true);
  });
});
