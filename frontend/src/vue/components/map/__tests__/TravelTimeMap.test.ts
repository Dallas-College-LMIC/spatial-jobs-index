import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import TravelTimeMap from '../TravelTimeMap.vue';

describe('TravelTimeMap', () => {
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
    wrapper = mount(TravelTimeMap);

    expect(wrapper.find('[data-testid="travel-time-map"]').exists()).toBe(true);
  });

  it('accepts travelTime prop', () => {
    wrapper = mount(TravelTimeMap, {
      props: { travelTime: 30 },
    });

    expect(wrapper.props('travelTime')).toBe(30);
  });
});
