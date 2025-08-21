import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import WageMap from '../WageMap.vue';

describe('WageMap', () => {
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
    wrapper = mount(WageMap);

    expect(wrapper.find('[data-testid="wage-map"]').exists()).toBe(true);
  });

  it('accepts wageLevel prop', () => {
    wrapper = mount(WageMap, {
      props: { wageLevel: 'high' },
    });

    expect(wrapper.props('wageLevel')).toBe('high');
  });
});
