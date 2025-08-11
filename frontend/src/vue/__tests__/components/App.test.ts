import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import App from '../../components/App.vue';

describe('App Component', () => {
  it('should mount successfully', () => {
    const wrapper = mount(App);
    expect(wrapper.exists()).toBe(true);
  });
});
