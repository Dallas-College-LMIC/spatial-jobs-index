import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import WagePage from '../WagePage.vue';

describe('WagePage', () => {
  const createWrapper = () => {
    return mount(WagePage, {
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
    expect(wrapper.find('h1').text()).toBe('Wage Level Analysis');
  });

  it('displays wage level selector', () => {
    const wrapper = createWrapper();
    expect(wrapper.find('[data-testid="wage-selector"]').exists()).toBe(true);
  });
});
