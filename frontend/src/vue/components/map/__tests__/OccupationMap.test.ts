import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import OccupationMap from '../OccupationMap.vue';

// Mock MapManager
vi.mock('../../../../js/mapUtils', () => ({
  MapManager: vi.fn().mockImplementation(() => ({
    addSource: vi.fn(),
    addLayer: vi.fn(),
    addPopupEvents: vi.fn(),
    onStyleLoad: vi.fn((callback) => callback()),
  })),
}));

describe('OccupationMap', () => {
  let wrapper: any;

  beforeEach(() => {
    setActivePinia(createPinia());
    wrapper = null;
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders map container', () => {
    wrapper = mount(OccupationMap, {
      global: {
        stubs: {
          // Stub out the map container to avoid Mapbox initialization in tests
        },
      },
    });

    expect(wrapper.find('[data-testid="occupation-map"]').exists()).toBe(true);
  });

  it('accepts occupationId prop', () => {
    wrapper = mount(OccupationMap, {
      props: { occupationId: '11-1011' },
    });

    expect(wrapper.props('occupationId')).toBe('11-1011');
  });

  it('shows loading indicator when store is loading', async () => {
    wrapper = mount(OccupationMap);
    const store = wrapper.vm.store;

    // Set loading state
    store.isLoading = true;
    await flushPromises();

    expect(wrapper.find('[data-testid="loading-indicator"]').exists()).toBe(true);
  });
});
