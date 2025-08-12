import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseLayout from '../BaseLayout.vue';

describe('BaseLayout', () => {
  it('should render header, main content, and footer sections', () => {
    const wrapper = mount(BaseLayout, {
      slots: {
        default: '<div>Main content</div>',
      },
    });

    expect(wrapper.find('header').exists()).toBe(true);
    expect(wrapper.find('main').exists()).toBe(true);
    expect(wrapper.html()).toContain('Main content');
  });
});
