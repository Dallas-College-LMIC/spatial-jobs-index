import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import AppHeader from '../AppHeader.vue';

describe('AppHeader', () => {
  it('renders the default title', () => {
    const wrapper = mount(AppHeader);
    expect(wrapper.text()).toContain('Spatial Jobs Index');
  });

  it('renders a custom title when provided', () => {
    const wrapper = mount(AppHeader, {
      props: {
        title: 'Custom Title',
      },
    });
    expect(wrapper.text()).toContain('Custom Title');
  });

  it('has a header element with correct class', () => {
    const wrapper = mount(AppHeader);
    expect(wrapper.find('header.app-header').exists()).toBe(true);
  });
});
