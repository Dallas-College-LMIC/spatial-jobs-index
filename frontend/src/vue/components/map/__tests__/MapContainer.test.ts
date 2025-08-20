import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import MapContainer from '../MapContainer.vue';
import mapboxgl from 'mapbox-gl';
import { MAP_CONFIG } from '../../../../js/constants';

// Mock mapbox-gl
vi.mock('mapbox-gl', () => ({
  default: {
    accessToken: '',
    Map: vi.fn().mockImplementation(() => ({
      on: vi.fn(),
      addControl: vi.fn(),
      resize: vi.fn(),
      remove: vi.fn(),
    })),
    NavigationControl: vi.fn(),
    FullscreenControl: vi.fn(),
  },
}));

describe('MapContainer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('renders a map container div', () => {
    const wrapper = mount(MapContainer);
    const mapDiv = wrapper.find('[data-testid="map-container"]');
    expect(mapDiv.exists()).toBe(true);
  });

  it('applies the correct container ID', () => {
    const containerId = 'test-map-id';
    const wrapper = mount(MapContainer, {
      props: { containerId },
    });
    const mapDiv = wrapper.find(`#${containerId}`);
    expect(mapDiv.exists()).toBe(true);
  });

  it('sets default container ID when not provided', () => {
    const wrapper = mount(MapContainer);
    const mapDiv = wrapper.find('#map');
    expect(mapDiv.exists()).toBe(true);
  });

  it('initializes mapbox with correct configuration', () => {
    mount(MapContainer);

    expect(mapboxgl.accessToken).toBe(MAP_CONFIG.accessToken);
    expect(mapboxgl.Map).toHaveBeenCalledWith(
      expect.objectContaining({
        container: 'map',
        style: MAP_CONFIG.style,
        center: MAP_CONFIG.center,
        zoom: MAP_CONFIG.zoom,
      })
    );
  });

  it('adds navigation controls to the map', () => {
    const mockAddControl = vi.fn();
    vi.mocked(mapboxgl.Map).mockImplementation(
      () =>
        ({
          on: vi.fn(),
          addControl: mockAddControl,
          resize: vi.fn(),
          remove: vi.fn(),
        }) as any
    );

    mount(MapContainer);

    expect(mapboxgl.NavigationControl).toHaveBeenCalled();
    expect(mapboxgl.FullscreenControl).toHaveBeenCalled();
    expect(mockAddControl).toHaveBeenCalledTimes(2);
  });

  it('emits map-loaded event when map style loads', async () => {
    const mockOn = vi.fn((event, callback) => {
      if (event === 'style.load') {
        callback();
      }
    });

    vi.mocked(mapboxgl.Map).mockImplementation(
      () =>
        ({
          on: mockOn,
          addControl: vi.fn(),
          resize: vi.fn(),
          remove: vi.fn(),
        }) as any
    );

    const wrapper = mount(MapContainer);

    expect(mockOn).toHaveBeenCalledWith('style.load', expect.any(Function));
    expect(wrapper.emitted('map-loaded')).toBeTruthy();
  });

  it('cleans up map on component unmount', () => {
    const mockRemove = vi.fn();
    vi.mocked(mapboxgl.Map).mockImplementation(
      () =>
        ({
          on: vi.fn(),
          addControl: vi.fn(),
          resize: vi.fn(),
          remove: mockRemove,
        }) as any
    );

    const wrapper = mount(MapContainer);
    wrapper.unmount();

    expect(mockRemove).toHaveBeenCalled();
  });
});
