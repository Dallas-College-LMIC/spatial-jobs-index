import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useMapLayers } from '../useMapLayers';

describe('useMapLayers', () => {
  let mockMap: any;

  beforeEach(() => {
    mockMap = {
      addLayer: vi.fn(),
      removeLayer: vi.fn(),
      getLayer: vi.fn(),
      setPaintProperty: vi.fn(),
      setLayoutProperty: vi.fn(),
      addSource: vi.fn(),
      getSource: vi.fn(),
    };
    vi.clearAllMocks();
  });

  it('should add a layer to the map', () => {
    const { addLayer } = useMapLayers(mockMap);

    const layer = {
      id: 'test-layer',
      type: 'fill',
      source: 'test-source',
      paint: {
        'fill-color': '#ff0000',
      },
    };

    addLayer(layer);

    expect(mockMap.addLayer).toHaveBeenCalledWith(layer);
  });

  it('should remove a layer from the map', () => {
    const { removeLayer } = useMapLayers(mockMap);

    removeLayer('test-layer');

    expect(mockMap.removeLayer).toHaveBeenCalledWith('test-layer');
  });

  it('should toggle layer visibility', () => {
    const { toggleLayerVisibility } = useMapLayers(mockMap);

    toggleLayerVisibility('test-layer', false);

    expect(mockMap.setLayoutProperty).toHaveBeenCalledWith('test-layer', 'visibility', 'none');

    toggleLayerVisibility('test-layer', true);

    expect(mockMap.setLayoutProperty).toHaveBeenCalledWith('test-layer', 'visibility', 'visible');
  });
});
