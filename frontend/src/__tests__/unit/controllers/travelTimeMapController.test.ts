import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import '../../mocks/mapbox-gl';
import type { MapClickEvent } from '../../../types/mapbox';

// Create hoisted mock for MapManager
const { mockMapManager, mockCanvas } = vi.hoisted(() => {
  // Create a canvas mock that maintains state
  const mockCanvas = {
    style: { cursor: '' },
  };
  const mockMapManager = {
    map: {
      on: vi.fn((event, layerOrCallback, callback?) => {
        // Store all handlers for testing
        if (typeof layerOrCallback === 'string' && callback) {
          mockMapManager._handlers = mockMapManager._handlers || {};
          mockMapManager._handlers[`${event}-${layerOrCallback}`] = callback;
        }
      }),
      off: vi.fn(),
      once: vi.fn(),
      addControl: vi.fn(),
      removeControl: vi.fn(),
      isStyleLoaded: vi.fn(() => true),
      addSource: vi.fn(),
      removeSource: vi.fn(),
      getSource: vi.fn(),
      addLayer: vi.fn(),
      removeLayer: vi.fn(),
      getLayer: vi.fn(() => null),
      setLayoutProperty: vi.fn(),
      setPaintProperty: vi.fn(),
      setFilter: vi.fn(),
      queryRenderedFeatures: vi.fn(),
      getCanvas: vi.fn(() => mockCanvas),
      remove: vi.fn(),
      resize: vi.fn(),
      fitBounds: vi.fn(),
      getZoom: vi.fn(() => 10),
      setZoom: vi.fn(),
      getCenter: vi.fn(() => ({ lng: -97.0336, lat: 32.8999 })),
      setCenter: vi.fn(),
      easeTo: vi.fn(),
      flyTo: vi.fn(),
      project: vi.fn(),
      unproject: vi.fn(),
    },
    containerId: 'test-container',
    popup: {} as any,
    initializeMap: vi.fn(),
    addControls: vi.fn(),
    createLayerColor: vi.fn(),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    clearLayers: vi.fn(),
    onStyleLoad: vi.fn((callback) => {
      // Call the callback immediately to simulate style load
      callback();
    }),
    addPopupEvents: vi.fn(),
    setLayerVisibility: vi.fn(),
    _handlers: {} as Record<string, Function>,
  };
  return { mockMapManager, mockCanvas };
});

// Mock dependencies
vi.mock('../../../js/mapUtils', () => ({
  MapManager: vi.fn(() => mockMapManager),
}));
vi.mock('../../../js/api');
vi.mock('../../../js/services/uiService', () => ({
  uiService: {
    showLoading: vi.fn(),
    hideLoading: vi.fn(),
    showError: vi.fn(),
    showNotification: vi.fn(),
  },
}));
vi.mock('../../../js/utils/errorHandler', () => ({
  ErrorHandler: {
    logError: vi.fn(),
    showInlineError: vi.fn(),
  },
}));

// Import after mocks
import { TravelTimeMapController } from '../../../js/controllers/TravelTimeMapController';
import { uiService } from '../../../js/services/uiService';
import { ErrorHandler } from '../../../js/utils/errorHandler';
import { mockGeoJSONResponse, mockIsochroneResponse } from '../../fixtures/apiResponses';

describe('TravelTimeMapController', () => {
  let controller: TravelTimeMapController;
  let mockApiService: any;

  beforeEach(async () => {
    vi.clearAllMocks();

    // Reset handlers and canvas
    mockMapManager._handlers = {};
    mockCanvas.style.cursor = '';

    // Setup DOM elements
    document.body.innerHTML = `
      <div id="test-container"></div>
      <div id="loading"></div>
      <div id="selected-tract" style="display: none;">
        <span id="tract-id"></span>
      </div>
      <button id="clear-selection" style="display: none;">Clear</button>
    `;

    // Create controller
    controller = new TravelTimeMapController('test-container');

    // Setup API service mock
    mockApiService = {
      getGeojsonData: vi.fn().mockResolvedValue(mockGeoJSONResponse),
      getIsochroneData: vi.fn().mockResolvedValue(mockIsochroneResponse),
      createAbortController: vi.fn(() => new AbortController()),
      cancelAllRequests: vi.fn(),
      cancelRequest: vi.fn(),
      getExportUrl: vi.fn().mockReturnValue('http://test.com/export'),
    };
    controller['apiService'] = mockApiService;

    // Wait for initialization
    await new Promise((resolve) => setTimeout(resolve, 10));
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('constructor and initialization', () => {
    it('should initialize with correct source IDs', () => {
      expect(controller['isochroneSourceId']).toBe('isochrones');
      expect(controller['sourceId']).toBe('census-tracts');
      expect(controller['isochroneLayers']).toEqual([]);
    });

    it('should initialize time band colors', () => {
      expect(controller['timeBandColors']).toEqual({
        '< 5': '#1a9850',
        '5 ~ 10': '#66bd63',
        '10 ~ 15': '#a6d96a',
        '15 ~ 20': '#fdae61',
        '20 ~ 25': '#fee08b',
        '25 ~ 30': '#f46d43',
        '30 ~ 45': '#d73027',
        '> 45': '#a50026',
      });
    });

    it('should handle initialization errors', async () => {
      const error = new Error('Init error');
      mockApiService.getGeojsonData.mockRejectedValue(error);

      // Create new controller with failing API
      const newController = new TravelTimeMapController('test-container');
      newController['apiService'] = mockApiService;
      newController['mapManager'] = mockMapManager;

      await newController.initialize();

      expect(ErrorHandler.logError).toHaveBeenCalledWith(error, 'Data Loading', {
        params: {},
        sourceId: 'census-tracts',
      });
    });
  });

  describe('initialize', () => {
    it('should add census tract and isochrone sources', async () => {
      await controller.initialize();

      expect(mockMapManager.addSource).toHaveBeenCalledWith('census-tracts', {
        type: 'FeatureCollection',
        features: [],
      });
      expect(mockMapManager.addSource).toHaveBeenCalledWith('isochrones', {
        type: 'FeatureCollection',
        features: [],
      });
    });

    it('should add census tract layers', async () => {
      await controller.initialize();

      expect(mockMapManager.map.addLayer).toHaveBeenCalledWith({
        id: 'census-tracts-fill',
        type: 'fill',
        source: 'census-tracts',
        paint: {
          'fill-color': 'transparent',
          'fill-opacity': 0,
        },
      });

      expect(mockMapManager.map.addLayer).toHaveBeenCalledWith({
        id: 'census-tracts-outline',
        type: 'line',
        source: 'census-tracts',
        paint: {
          'line-color': '#cccccc',
          'line-width': 0.5,
          'line-opacity': 0.8,
        },
      });

      expect(mockMapManager.map.addLayer).toHaveBeenCalledWith({
        id: 'census-tracts-hover',
        type: 'line',
        source: 'census-tracts',
        paint: {
          'line-color': '#000000',
          'line-width': 2,
          'line-opacity': 1,
        },
        filter: ['==', 'geoid', ''],
      });

      expect(mockMapManager.map.addLayer).toHaveBeenCalledWith({
        id: 'selected-tract',
        type: 'line',
        source: 'census-tracts',
        paint: {
          'line-color': '#000000',
          'line-width': 3,
          'line-opacity': 1,
        },
        filter: ['==', 'geoid', ''],
      });
    });

    it('should setup click handlers', async () => {
      await controller.initialize();

      // Check that the setup was called after timeout
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      expect(mockMapManager.map.on).toHaveBeenCalledWith(
        'click',
        expect.any(Function)
      );
      expect(mockMapManager.map.on).toHaveBeenCalledWith(
        'mousemove',
        'census-tracts-fill',
        expect.any(Function)
      );
      expect(mockMapManager.map.on).toHaveBeenCalledWith(
        'mouseleave',
        'census-tracts-fill',
        expect.any(Function)
      );
    });
  });

  describe('census tract click handling', () => {
    it('should handle census tract click', async () => {
      await controller.initialize();

      // Mock queryRenderedFeatures to return a feature
      mockMapManager.map.queryRenderedFeatures.mockReturnValue([
        {
          properties: { geoid: '48001950100.0' },
        },
      ]);

      const mockEvent = {
        point: { x: 100, y: 100 },
      } as any;

      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      // Get the click handler from the mock
      const clickHandler = mockMapManager.map.on.mock.calls.find(
        call => call[0] === 'click' && typeof call[1] === 'function'
      )?.[1];
      expect(clickHandler).toBeDefined();
      await clickHandler(mockEvent);

      // Check selected tract display was updated
      const tractIdSpan = document.getElementById('tract-id');
      const selectedTractDiv = document.getElementById('selected-tract');
      const clearButton = document.getElementById('clear-selection');

      expect(tractIdSpan?.textContent).toBe('48001950100');
      expect(selectedTractDiv?.style.display).toBe('block');
      expect(clearButton?.style.display).toBe('block');

      // Check filter was set (with .0 suffix for the filter)
      expect(mockMapManager.map.setFilter).toHaveBeenCalledWith('selected-tract', [
        '==',
        'geoid',
        '48001950100.0',
      ]);

      // Check isochrone data was loaded
      expect(mockApiService.getIsochroneData).toHaveBeenCalledWith(
        '48001950100',
        expect.any(AbortSignal)
      );
    });

    it('should handle click with no features', async () => {
      await controller.initialize();

      // Mock queryRenderedFeatures to return no features
      mockMapManager.map.queryRenderedFeatures.mockReturnValue([]);

      const mockEvent = {
        point: { x: 100, y: 100 },
      } as any;

      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      const clickHandler = mockMapManager.map.on.mock.calls.find(
        call => call[0] === 'click' && typeof call[1] === 'function'
      )?.[1];
      await clickHandler(mockEvent);

      expect(mockApiService.getIsochroneData).not.toHaveBeenCalled();
    });

    it('should handle click with no GEOID', async () => {
      await controller.initialize();

      // Mock queryRenderedFeatures to return a feature without GEOID
      mockMapManager.map.queryRenderedFeatures.mockReturnValue([
        {
          properties: {},
        },
      ]);

      const mockEvent = {
        point: { x: 100, y: 100 },
      } as any;

      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      const clickHandler = mockMapManager.map.on.mock.calls.find(
        call => call[0] === 'click' && typeof call[1] === 'function'
      )?.[1];
      await clickHandler(mockEvent);

      expect(mockApiService.getIsochroneData).not.toHaveBeenCalled();
    });

    it('should prevent multiple simultaneous requests', async () => {
      await controller.initialize();
      controller['isLoading'] = true;

      // Mock queryRenderedFeatures to return a feature
      mockMapManager.map.queryRenderedFeatures.mockReturnValue([
        {
          properties: { geoid: '48001950100.0' },
        },
      ]);

      const mockEvent = {
        point: { x: 100, y: 100 },
      } as any;

      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      const clickHandler = mockMapManager.map.on.mock.calls.find(
        call => call[0] === 'click' && typeof call[1] === 'function'
      )?.[1];
      await clickHandler(mockEvent);

      expect(mockApiService.getIsochroneData).not.toHaveBeenCalled();
    });
  });

  describe('isochrone data loading', () => {
    it('should load and display isochrone data', async () => {
      await controller['loadIsochroneData']('48001950100');

      expect(uiService.showLoading).toHaveBeenCalledWith('loading', {
        message: 'Loading travel times...',
      });
      expect(mockApiService.getIsochroneData).toHaveBeenCalledWith(
        '48001950100',
        expect.any(AbortSignal)
      );
      expect(mockMapManager.addSource).toHaveBeenCalledWith('isochrones', mockIsochroneResponse);
      expect(uiService.hideLoading).toHaveBeenCalledWith('loading');
    });

    it('should add isochrone layers in correct order', async () => {
      await controller['loadIsochroneData']('48001950100');

      // Check layers were added in reverse order
      const expectedTimeBands = [
        '> 45',
        '30 ~ 45',
        '25 ~ 30',
        '20 ~ 25',
        '15 ~ 20',
        '10 ~ 15',
        '5 ~ 10',
        '< 5',
      ];

      expectedTimeBands.forEach((timeBand) => {
        const layerId = `isochrone-${timeBand.replace(/[<> ~]/g, '-')}`;
        expect(mockMapManager.map.addLayer).toHaveBeenCalledWith(
          {
            id: layerId,
            type: 'fill',
            source: 'isochrones',
            paint: {
              'fill-color': controller['timeBandColors'][timeBand],
              'fill-opacity': 0.6,
            },
            filter: ['==', 'time_category', timeBand],
          },
          'census-tracts-outline'
        );
      });

      // Check outline layer was added
      expect(mockMapManager.map.addLayer).toHaveBeenCalledWith(
        {
          id: 'isochrone-outline',
          type: 'line',
          source: 'isochrones',
          paint: {
            'line-color': '#333333',
            'line-width': 1,
            'line-opacity': 0.8,
          },
        },
        'census-tracts-hover'
      );
    });

    it('should handle API errors', async () => {
      const error = new Error('API Error');
      mockApiService.getIsochroneData.mockRejectedValue(error);

      await controller['loadIsochroneData']('48001950100');

      expect(ErrorHandler.logError).toHaveBeenCalledWith(error, 'Isochrone Data Loading', {
        geoid: '48001950100',
      });
      expect(ErrorHandler.showInlineError).toHaveBeenCalledWith(
        'test-container',
        'Failed to load travel time data for tract 48001950100. Click to retry.',
        expect.any(Function)
      );
    });

    it('should handle abort errors gracefully', async () => {
      const abortError = new Error('Aborted');
      abortError.name = 'AbortError';
      mockApiService.getIsochroneData.mockRejectedValue(abortError);

      await controller['loadIsochroneData']('48001950100');

      expect(ErrorHandler.logError).not.toHaveBeenCalled();
      expect(ErrorHandler.showInlineError).not.toHaveBeenCalled();
    });

    it('should clear existing isochrone layers before adding new ones', async () => {
      // Add some existing layers
      controller['isochroneLayers'] = ['existing-layer-1', 'existing-layer-2'];
      mockMapManager.map.getLayer = vi.fn().mockReturnValue(true);

      await controller['loadIsochroneData']('48001950100');

      expect(mockMapManager.map.removeLayer).toHaveBeenCalledWith('existing-layer-1');
      expect(mockMapManager.map.removeLayer).toHaveBeenCalledWith('existing-layer-2');
    });
  });

  describe('clearSelection', () => {
    it('should clear all selections and layers', () => {
      // Setup initial state
      controller['isochroneLayers'] = ['layer1', 'layer2'];
      mockMapManager.map.getLayer = vi.fn().mockReturnValue(true);

      controller['clearSelection']();

      // Check tract filter was cleared
      expect(mockMapManager.map.setFilter).toHaveBeenCalledWith('selected-tract', [
        '==',
        'geoid',
        '',
      ]);

      // Check isochrone layers were removed
      expect(mockMapManager.map.removeLayer).toHaveBeenCalledWith('layer1');
      expect(mockMapManager.map.removeLayer).toHaveBeenCalledWith('layer2');

      // Check isochrone source was reset
      expect(mockMapManager.addSource).toHaveBeenCalledWith('isochrones', {
        type: 'FeatureCollection',
        features: [],
      });

      // Check UI was updated
      const selectedTractDiv = document.getElementById('selected-tract');
      const clearButton = document.getElementById('clear-selection');
      expect(selectedTractDiv?.style.display).toBe('none');
      expect(clearButton?.style.display).toBe('none');
    });

    it('should cancel ongoing requests', () => {
      const mockController = {
        signal: { aborted: false },
        abort: vi.fn(),
      };
      controller['currentLoadController'] = mockController as any;

      controller['clearSelection']();

      // The controller should abort the request directly
      expect(mockController.abort).toHaveBeenCalled();
    });
  });

  describe('clear button functionality', () => {
    it('should setup clear button click handler', async () => {
      await controller.initialize();

      const clearButton = document.getElementById('clear-selection');
      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      const clearSelectionSpy = vi.spyOn(controller as any, 'clearSelection');

      clearButton?.click();

      expect(clearSelectionSpy).toHaveBeenCalled();
    });

    it('should handle missing clear button gracefully', async () => {
      document.getElementById('clear-selection')?.remove();

      // Should not throw
      await expect(controller.initialize()).resolves.not.toThrow();
    });
  });

  describe('loading state management', () => {
    it('should manage loading state correctly', async () => {
      // Initially not loading
      expect(controller['isLoading']).toBe(false);

      // Start a load
      await controller['loadIsochroneData']('48001950100');

      // Should not be loading after completion
      expect(controller['isLoading']).toBe(false);

      // Verify the API was called
      expect(mockApiService.getIsochroneData).toHaveBeenCalledTimes(1);
    });

    it('should reset loading state on error', async () => {
      mockApiService.getIsochroneData.mockRejectedValue(new Error('Test error'));

      await controller['loadIsochroneData']('48001950100');

      expect(controller['isLoading']).toBe(false);
    });
  });

  describe('UI updates', () => {
    it('should update selected tract display correctly', () => {
      controller['updateSelectedTractDisplay']('48001950100');

      const tractIdSpan = document.getElementById('tract-id');
      const selectedTractDiv = document.getElementById('selected-tract');
      const clearButton = document.getElementById('clear-selection');

      expect(tractIdSpan?.textContent).toBe('48001950100');
      expect(selectedTractDiv?.style.display).toBe('block');
      expect(clearButton?.style.display).toBe('block');
    });

    it('should hide selected tract display when null', () => {
      controller['updateSelectedTractDisplay'](null);

      const selectedTractDiv = document.getElementById('selected-tract');
      const clearButton = document.getElementById('clear-selection');

      expect(selectedTractDiv?.style.display).toBe('none');
      expect(clearButton?.style.display).toBe('none');
    });

    it('should handle missing UI elements gracefully', () => {
      document.getElementById('selected-tract')?.remove();
      document.getElementById('tract-id')?.remove();
      document.getElementById('clear-selection')?.remove();

      // Should not throw
      expect(() => controller['updateSelectedTractDisplay']('48001950100')).not.toThrow();
    });
  });

  describe('getLayerIds', () => {
    it('should return all layer IDs', () => {
      controller['isochroneLayers'] = ['iso-layer-1', 'iso-layer-2'];

      const layerIds = controller['getLayerIds']();

      expect(layerIds).toEqual([
        'census-tracts-fill',
        'census-tracts-outline',
        'census-tracts-hover',
        'selected-tract',
        'iso-layer-1',
        'iso-layer-2',
      ]);
    });
  });

  describe('cursor handling', () => {
    it('should change cursor on mousemove', async () => {
      await controller.initialize();
      
      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));

      // Get and call the mousemove handler
      const mousemoveHandler = mockMapManager._handlers['mousemove-census-tracts-fill'];
      expect(mousemoveHandler).toBeDefined();
      
      const mockEvent = {
        features: [{
          properties: { geoid: '48001950100.0' }
        }]
      };
      mousemoveHandler(mockEvent);

      expect(mockCanvas.style.cursor).toBe('pointer');
    });

    it('should reset cursor on mouseleave', async () => {
      await controller.initialize();
      
      // Wait for setup to complete
      await new Promise((resolve) => setTimeout(resolve, 200));

      // Set cursor to pointer first
      mockCanvas.style.cursor = 'pointer';

      // Get and call the mouseleave handler
      const mouseleaveHandler = mockMapManager._handlers['mouseleave-census-tracts-fill'];
      expect(mouseleaveHandler).toBeDefined();
      mouseleaveHandler();

      expect(mockCanvas.style.cursor).toBe('');
    });
  });
});

