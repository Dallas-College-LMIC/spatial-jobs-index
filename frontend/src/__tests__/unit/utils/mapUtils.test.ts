import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import '../../mocks/mapbox-gl';
import { mockMap, mockPopup } from '../../mocks/mapbox-gl';
import { MapManager } from '../../../js/mapUtils';
import { MAP_CONFIG, COLOR_SCHEMES } from '../../../js/constants';
import type { GeoJSONResponse } from '../../../types/api';

// Mock the constants
vi.mock('../../../js/constants', () => ({
  MAP_CONFIG: {
    accessToken: 'test-token',
    style: 'mapbox://styles/mapbox/light-v10',
    center: [-97.0336, 32.8999],
    zoom: 8.5,
  },
  COLOR_SCHEMES: {
    zscoreCategories: ['very_low', 'low', 'medium', 'high', 'very_high'],
    zscoreColors: ['#d73027', '#f46d43', '#fee08b', '#74add1', '#313695'],
    outlineColor: '#ffffff',
  },
}));

describe('MapManager', () => {
  let mapManager: MapManager;

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup DOM
    document.body.innerHTML = '<div id="test-container"></div>';

    // Reset mock functions
    mockMap.getSource.mockReturnValue(null);
    mockMap.getLayer.mockReturnValue(null);
    mockMap.on.mockClear();
    mockMap.addControl.mockClear();
    mockMap.addSource.mockClear();
    mockMap.addLayer.mockClear();
    mockMap.removeLayer.mockClear();
    mockMap.setLayoutProperty.mockClear();
    mockMap.getCanvas.mockReturnValue({ style: { cursor: '' } });

    mockPopup.setLngLat.mockClear().mockReturnThis();
    mockPopup.setHTML.mockClear().mockReturnThis();
    mockPopup.addTo.mockClear().mockReturnThis();

    // Ensure Map constructor returns mockMap
    (globalThis as any).mapboxgl.Map.mockImplementation(() => mockMap);
    (globalThis as any).mapboxgl.Popup.mockImplementation(() => mockPopup);

    // Create MapManager instance
    mapManager = new MapManager('test-container');

    // Verify the popup was assigned correctly
    expect((mapManager as any).popup).toBe(mockPopup);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('constructor and initialization', () => {
    it('should initialize with correct container ID', () => {
      expect(mapManager).toBeDefined();
      expect((globalThis as any).mapboxgl.accessToken).toBe('test-token');
    });

    it('should create map with correct configuration', () => {
      expect((globalThis as any).mapboxgl.Map).toHaveBeenCalledWith({
        container: 'test-container',
        ...MAP_CONFIG,
      });
    });

    it('should create popup with correct configuration', () => {
      expect((globalThis as any).mapboxgl.Popup).toHaveBeenCalledWith({
        closeButton: true,
        closeOnClick: false,
        anchor: 'bottom',
        offset: 0,
        maxWidth: 'none',
      });
    });

    it('should add navigation and fullscreen controls', () => {
      expect((globalThis as any).mapboxgl.FullscreenControl).toHaveBeenCalledWith({
        container: document.querySelector('body'),
      });
      expect((globalThis as any).mapboxgl.NavigationControl).toHaveBeenCalledWith({
        showCompass: true,
        showZoom: true,
        visualizePitch: true,
      });
      expect(mockMap.addControl).toHaveBeenCalledTimes(2);
    });
  });

  describe('addSource', () => {
    const mockGeoJSONData: GeoJSONResponse = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [
              [
                [-97, 32],
                [-96, 32],
                [-96, 33],
                [-97, 33],
                [-97, 32],
              ],
            ],
          },
          properties: {
            GEOID: '12345',
            test_zscore: 1.5,
          },
        },
      ],
    };

    it('should add new source when source does not exist', () => {
      mockMap.getSource.mockReturnValue(null);

      mapManager.addSource('test-source', mockGeoJSONData);

      expect(mockMap.getSource).toHaveBeenCalledWith('test-source');
      expect(mockMap.addSource).toHaveBeenCalledWith('test-source', {
        type: 'geojson',
        data: mockGeoJSONData,
      });
    });

    it('should update existing source when source exists', () => {
      const mockExistingSource = {
        type: 'geojson',
        setData: vi.fn(),
      };
      mockMap.getSource.mockReturnValue(mockExistingSource);

      mapManager.addSource('test-source', mockGeoJSONData);

      expect(mockMap.getSource).toHaveBeenCalledWith('test-source');
      expect(mockExistingSource.setData).toHaveBeenCalledWith(mockGeoJSONData);
      expect(mockMap.addSource).not.toHaveBeenCalled();
    });

    it('should handle non-GeoJSON source by adding new source', () => {
      const mockNonGeoJSONSource = {
        // Missing setData method
      };
      mockMap.getSource.mockReturnValue(mockNonGeoJSONSource);

      mapManager.addSource('test-source', mockGeoJSONData);

      expect(mockMap.addSource).toHaveBeenCalledWith('test-source', {
        type: 'geojson',
        data: mockGeoJSONData,
      });
    });
  });

  describe('addLayer', () => {
    it('should remove existing layer before adding new one', () => {
      mockMap.getLayer.mockReturnValue({ id: 'test-layer' });

      mapManager.addLayer('test-layer', 'test-source', 'test_property');

      expect(mockMap.getLayer).toHaveBeenCalledWith('test-layer');
      expect(mockMap.removeLayer).toHaveBeenCalledWith('test-layer');
    });

    it('should add layer with correct configuration', () => {
      mockMap.getLayer.mockReturnValue(null);

      mapManager.addLayer('test-layer', 'test-source', 'test_property', 'visible');

      expect(mockMap.addLayer).toHaveBeenCalledWith({
        id: 'test-layer',
        type: 'fill',
        source: 'test-source',
        layout: {
          visibility: 'visible',
        },
        paint: {
          'fill-color': expect.any(Array),
          'fill-outline-color': COLOR_SCHEMES.outlineColor,
        },
      });
    });

    it('should use default visibility when not specified', () => {
      mockMap.getLayer.mockReturnValue(null);

      mapManager.addLayer('test-layer', 'test-source', 'test_property');

      const addLayerCall = mockMap.addLayer.mock.calls[0]?.[0];
      expect(addLayerCall).toBeDefined();
      expect(addLayerCall?.layout?.visibility).toBe('visible');
    });

    it('should create correct color expression', () => {
      mockMap.getLayer.mockReturnValue(null);

      mapManager.addLayer('test-layer', 'test-source', 'test_property');

      const addLayerCall = mockMap.addLayer.mock.calls[0]?.[0];
      expect(addLayerCall).toBeDefined();
      const fillColor = addLayerCall?.paint?.['fill-color'];

      expect(fillColor).toEqual([
        'match',
        ['get', 'test_property'],
        'very_low',
        '#d73027',
        'low',
        '#f46d43',
        'medium',
        '#fee08b',
        'high',
        '#74add1',
        'very_high',
        '#313695',
        '#000000',
      ]);
    });
  });

  describe('setLayerVisibility', () => {
    it('should set layer visibility when layer exists', () => {
      mockMap.getLayer.mockReturnValue({ id: 'test-layer' });

      mapManager.setLayerVisibility('test-layer', 'none');

      expect(mockMap.getLayer).toHaveBeenCalledWith('test-layer');
      expect(mockMap.setLayoutProperty).toHaveBeenCalledWith('test-layer', 'visibility', 'none');
    });

    it('should not set visibility when layer does not exist', () => {
      mockMap.getLayer.mockReturnValue(null);

      mapManager.setLayerVisibility('test-layer', 'visible');

      expect(mockMap.getLayer).toHaveBeenCalledWith('test-layer');
      expect(mockMap.setLayoutProperty).not.toHaveBeenCalled();
    });
  });

  describe('addPopupEvents', () => {
    beforeEach(() => {
      mockMap.on = vi.fn();
      mockMap.getCanvas = vi.fn(() => ({
        style: { cursor: '' },
      }));
    });

    it('should add click event listener', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      expect(mockMap.on).toHaveBeenCalledWith('click', 'test-layer', expect.any(Function));
    });

    it('should add mouseenter event listener', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      expect(mockMap.on).toHaveBeenCalledWith('mouseenter', 'test-layer', expect.any(Function));
    });

    it('should add mouseleave event listener', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      expect(mockMap.on).toHaveBeenCalledWith('mouseleave', 'test-layer', expect.any(Function));
    });

    it('should handle click event with valid features', () => {
      // Verify popup was created during initialization
      expect((mapManager as any).popup).toBeDefined();

      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      const clickCall = mockMap.on.mock.calls.find((call) => call[0] === 'click');
      expect(clickCall).toBeDefined();
      const clickHandler = clickCall![2];
      const mockEvent = {
        lngLat: { lng: -97, lat: 32 },
        features: [
          {
            properties: {
              GEOID: '12345',
              test_score: 1.234,
            },
          },
        ],
      };

      clickHandler?.(mockEvent);

      expect(mockPopup.setLngLat).toHaveBeenCalledWith({ lng: -97, lat: 32 });
      expect(mockPopup.setHTML).toHaveBeenCalledWith(
        expect.stringContaining('Tract: </b><span>12345</span>')
      );
      expect(mockPopup.setHTML).toHaveBeenCalledWith(
        expect.stringContaining('Test Title: </b><span>1.23</span>')
      );
      expect(mockPopup.addTo).toHaveBeenCalledWith(mockMap);
    });

    it('should handle click event with no features', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      const clickCall = mockMap.on.mock.calls.find((call) => call[0] === 'click');
      expect(clickCall).toBeDefined();
      const clickHandler = clickCall![2];
      const mockEvent = {
        lngLat: { lng: -97, lat: 32 },
        features: [],
      };

      clickHandler?.(mockEvent);

      expect(mockPopup.setLngLat).not.toHaveBeenCalled();
    });

    it('should handle click event with undefined score', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      const clickCall = mockMap.on.mock.calls.find((call) => call[0] === 'click');
      expect(clickCall).toBeDefined();
      const clickHandler = clickCall![2];
      const mockEvent = {
        lngLat: { lng: -97, lat: 32 },
        features: [
          {
            properties: {
              GEOID: '12345',
              test_score: undefined,
            },
          },
        ],
      };

      clickHandler?.(mockEvent);

      expect(mockPopup.setHTML).toHaveBeenCalledWith(
        expect.stringContaining('Test Title: </b><span>N/A</span>')
      );
    });

    it('should handle mouseenter event', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      const mouseenterCall = mockMap.on.mock.calls.find((call) => call[0] === 'mouseenter');
      expect(mouseenterCall).toBeDefined();
      const mouseenterHandler = mouseenterCall![2];
      const mockCanvas = { style: { cursor: '' } };
      mockMap.getCanvas.mockReturnValue(mockCanvas);

      mouseenterHandler?.();

      expect(mockMap.getCanvas).toHaveBeenCalled();
      expect(mockCanvas.style.cursor).toBe('pointer');
    });

    it('should handle mouseleave event', () => {
      mapManager.addPopupEvents('test-layer', 'Test Title', 'test_score');

      const mouseleaveCall = mockMap.on.mock.calls.find((call) => call[0] === 'mouseleave');
      expect(mouseleaveCall).toBeDefined();
      const mouseleaveHandler = mouseleaveCall![2];
      const mockCanvas = { style: { cursor: 'pointer' } };
      mockMap.getCanvas.mockReturnValue(mockCanvas);

      mouseleaveHandler?.();

      expect(mockMap.getCanvas).toHaveBeenCalled();
      expect(mockCanvas.style.cursor).toBe('');
    });
  });

  describe('onStyleLoad', () => {
    it('should register style.load event listener', () => {
      const mockCallback = vi.fn();

      mapManager.onStyleLoad(mockCallback);

      expect(mockMap.on).toHaveBeenCalledWith('style.load', mockCallback);
    });
  });
});
