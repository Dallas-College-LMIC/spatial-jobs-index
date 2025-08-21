import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import TravelTimePage from '../TravelTimePage.vue';

describe('TravelTimePage', () => {
  const createWrapper = () => {
    return mount(TravelTimePage, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          'router-link': true,
          'router-view': true,
        },
      },
    });
  };

  it('renders the page title', () => {
    const wrapper = createWrapper();
    expect(wrapper.find('h1').text()).toBe('Travel Time Analysis');
  });

  it('displays travel time input', () => {
    const wrapper = createWrapper();
    expect(wrapper.find('[data-testid="travel-time-input"]').exists()).toBe(true);
  });
});
