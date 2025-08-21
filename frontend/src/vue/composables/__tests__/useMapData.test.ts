import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useMapData } from '../useMapData';

describe('useMapData', () => {
  let mockMap: any;

  beforeEach(() => {
    mockMap = {
      addSource: vi.fn(),
      removeSource: vi.fn(),
      getSource: vi.fn(),
      setData: vi.fn(),
    };
    vi.clearAllMocks();
  });

  it('should add data source to map', () => {
    const { addDataSource } = useMapData(mockMap);

    const sourceData = {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: [],
      },
    };

    addDataSource('test-source', sourceData);

    expect(mockMap.addSource).toHaveBeenCalledWith('test-source', sourceData);
  });

  it('should update source data', () => {
    const mockSource = {
      setData: vi.fn(),
    };
    mockMap.getSource.mockReturnValue(mockSource);

    const { updateSourceData } = useMapData(mockMap);

    const newData = {
      type: 'FeatureCollection',
      features: [{ type: 'Feature', properties: {}, geometry: null }],
    };

    updateSourceData('test-source', newData);

    expect(mockMap.getSource).toHaveBeenCalledWith('test-source');
    expect(mockSource.setData).toHaveBeenCalledWith(newData);
  });
});
