import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useMapbox } from '../useMapbox';
import mapboxgl from 'mapbox-gl';

// Mock mapbox-gl
vi.mock('mapbox-gl', () => ({
  default: {
    Map: vi.fn(),
    NavigationControl: vi.fn(),
    FullscreenControl: vi.fn(),
    accessToken: '',
  },
}));

describe('useMapbox', () => {
  let container: HTMLElement;

  beforeEach(() => {
    container = document.createElement('div');
    container.id = 'map-container';
    document.body.appendChild(container);
    vi.clearAllMocks();
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  it('should initialize map with correct config', async () => {
    const mockMap = {
      on: vi.fn((event, callback) => {
        if (event === 'load') {
          setTimeout(callback, 0);
        }
      }),
      remove: vi.fn(),
      addControl: vi.fn(),
    };
    (mapboxgl.Map as any).mockReturnValue(mockMap);

    const { initializeMap, map } = useMapbox();

    await initializeMap(container, {
      center: [-96.8, 32.8],
      zoom: 10,
    });

    expect(mapboxgl.Map).toHaveBeenCalledWith({
      container,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [-96.8, 32.8],
      zoom: 10,
    });
    expect(map.value).toEqual(mockMap);
  });

  it('should add navigation control when specified', async () => {
    const mockMap = {
      on: vi.fn((event, callback) => {
        if (event === 'load') {
          setTimeout(callback, 0);
        }
      }),
      remove: vi.fn(),
      addControl: vi.fn(),
    };
    const mockNavControl = {};

    (mapboxgl.Map as any).mockReturnValue(mockMap);
    (mapboxgl.NavigationControl as any).mockReturnValue(mockNavControl);

    const { initializeMap } = useMapbox();

    await initializeMap(container, {
      center: [-96.8, 32.8],
      zoom: 10,
      controls: { navigation: true },
    });

    expect(mapboxgl.NavigationControl).toHaveBeenCalled();
    expect(mockMap.addControl).toHaveBeenCalledWith(mockNavControl);
  });

  it('should handle map load event', async () => {
    const mockMap = {
      on: vi.fn((event, callback) => {
        if (event === 'load') {
          setTimeout(callback, 0);
        }
      }),
      remove: vi.fn(),
      addControl: vi.fn(),
    };
    (mapboxgl.Map as any).mockReturnValue(mockMap);

    const { initializeMap, isMapLoaded } = useMapbox();

    const result = await initializeMap(container);

    expect(isMapLoaded.value).toBe(true);
    expect(result).toEqual(mockMap);
  });

  it('should clean up map on destroy', async () => {
    const mockMap = {
      on: vi.fn((event, callback) => {
        if (event === 'load') {
          setTimeout(callback, 0);
        }
      }),
      remove: vi.fn(),
      addControl: vi.fn(),
    };
    (mapboxgl.Map as any).mockReturnValue(mockMap);

    const { initializeMap, destroyMap } = useMapbox();

    await initializeMap(container);
    destroyMap();

    expect(mockMap.remove).toHaveBeenCalled();
  });
});
