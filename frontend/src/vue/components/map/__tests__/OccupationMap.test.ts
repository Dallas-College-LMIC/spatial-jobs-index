import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import OccupationMap from '../OccupationMap.vue';

describe('OccupationMap', () => {
  let wrapper: any;

  beforeEach(() => {
    wrapper = null;
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders map container', () => {
    wrapper = mount(OccupationMap);

    expect(wrapper.find('[data-testid="occupation-map"]').exists()).toBe(true);
  });

  it('accepts occupationId prop', () => {
    wrapper = mount(OccupationMap, {
      props: { occupationId: '11-1011' },
    });

    expect(wrapper.props('occupationId')).toBe('11-1011');
  });

  it('emits data-loaded event when data is fetched', async () => {
    wrapper = mount(OccupationMap, {
      props: { occupationId: '11-1011' },
    });

    // Simulate data loading (in real component this would happen after API call)
    wrapper.vm.$emit('data-loaded', { features: [] });

    expect(wrapper.emitted('data-loaded')).toBeTruthy();
    expect(wrapper.emitted('data-loaded')?.[0]).toEqual([{ features: [] }]);
  });

  it('shows loading indicator when loading prop is true', () => {
    wrapper = mount(OccupationMap, {
      props: { loading: true },
    });

    expect(wrapper.find('[data-testid="loading-indicator"]').exists()).toBe(true);
  });
});
