import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useMapStore } from '../map';
import type { Map } from 'mapbox-gl';

// Mock mapbox-gl
vi.mock('mapbox-gl', () => ({
  Map: vi.fn(),
}));

describe('Map Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  describe('Map Instance Management', () => {
    it('should initialize with null map instance', () => {
      const store = useMapStore();
      expect(store.mapInstance).toBeNull();
    });

    it('should set and get map instance', () => {
      const store = useMapStore();
      const mockMap = { id: 'test-map' } as unknown as Map;

      store.setMapInstance(mockMap);
      expect(store.mapInstance).toEqual(mockMap);
    });

    it('should track map loaded state', () => {
      const store = useMapStore();
      expect(store.isMapLoaded).toBe(false);

      store.setMapLoaded(true);
      expect(store.isMapLoaded).toBe(true);
    });
  });

  describe('Layer Management', () => {
    it('should track active layers', () => {
      const store = useMapStore();
      expect(store.activeLayers).toEqual([]);
    });

    it('should add a layer', () => {
      const store = useMapStore();
      store.addLayer('occupation-layer');

      expect(store.activeLayers).toContain('occupation-layer');
    });

    it('should remove a layer', () => {
      const store = useMapStore();
      store.addLayer('occupation-layer');
      store.addLayer('wage-layer');

      store.removeLayer('occupation-layer');

      expect(store.activeLayers).not.toContain('occupation-layer');
      expect(store.activeLayers).toContain('wage-layer');
    });
  });

  describe('Source Management', () => {
    it('should track data sources', () => {
      const store = useMapStore();
      expect(store.dataSources).toEqual({});
    });

    it('should add a data source', () => {
      const store = useMapStore();
      const sourceData = { type: 'geojson', data: { type: 'FeatureCollection', features: [] } };

      store.addSource('occupation-source', sourceData);

      expect(store.dataSources['occupation-source']).toEqual(sourceData);
    });
  });

  describe('Popup Management', () => {
    it('should track popup state', () => {
      const store = useMapStore();
      expect(store.isPopupOpen).toBe(false);
      expect(store.popupContent).toBeNull();
    });
  });
});
