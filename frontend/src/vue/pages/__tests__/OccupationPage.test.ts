import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import OccupationPage from '../OccupationPage.vue';

describe('OccupationPage', () => {
  it('should render page title', () => {
    const wrapper = mount(OccupationPage, {
      global: {
        plugins: [createTestingPinia()],
      },
    });

    expect(wrapper.find('h1').text()).toBe('Occupation Access');
  });

  it('should render occupation select component', () => {
    const wrapper = mount(OccupationPage, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          OccupationSelect: true,
        },
      },
    });

    expect(wrapper.findComponent({ name: 'OccupationSelect' }).exists()).toBe(true);
  });
});
