import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import MapContainer from '../MapContainer.vue';

// Mock mapbox-gl
vi.mock('mapbox-gl', () => ({
  default: {
    accessToken: '',
    Map: vi.fn().mockImplementation(() => ({
      on: vi.fn((event, callback) => {
        if (event === 'style.load') {
          setTimeout(callback, 0);
        }
      }),
      addControl: vi.fn(),
      remove: vi.fn(),
    })),
    NavigationControl: vi.fn(),
    FullscreenControl: vi.fn(),
  },
}));

describe('MapContainer Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize map with proper configuration', async () => {
    const wrapper = mount(MapContainer, {
      props: {
        containerId: 'test-map',
      },
    });

    await wrapper.vm.$nextTick();

    // Check that map container is rendered
    expect(wrapper.find('#test-map').exists()).toBe(true);
    expect(wrapper.find('[data-testid="map-container"]').exists()).toBe(true);
  });
});
