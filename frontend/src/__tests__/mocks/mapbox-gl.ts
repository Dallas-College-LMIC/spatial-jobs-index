import { vi } from 'vitest';

// Mock map instance
export const mockMap = {
  on: vi.fn((...args) => {
    const event = args[0];
    if (event === 'load') {
      // For 'load' event, callback is at index 1
      setTimeout(args[1], 0);
    }
    // For layer-specific events, callback is at index 2
    // This mock stores all arguments for test verification
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
  getLayer: vi.fn(),
  setLayoutProperty: vi.fn(),
  setPaintProperty: vi.fn(),
  setFilter: vi.fn(),
  queryRenderedFeatures: vi.fn(),
  getCanvas: vi.fn(() => ({
    style: { cursor: '' },
  })),
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
};

// Mock popup instance
export const mockPopup = {
  setLngLat: vi.fn().mockReturnThis(),
  setHTML: vi.fn().mockReturnThis(),
  addTo: vi.fn().mockReturnThis(),
  remove: vi.fn().mockReturnThis(),
  isOpen: vi.fn(() => false),
};

// Create a reference that can be used in tests
export const mockMapboxGL = {
  Map: vi.fn(() => mockMap),
  Popup: vi.fn(() => mockPopup),
  NavigationControl: vi.fn(() => ({})),
  FullscreenControl: vi.fn(() => ({})),
  accessToken: '',
  supported: vi.fn(() => true),
  LngLat: vi.fn((lng: number, lat: number) => ({ lng, lat })),
  LngLatBounds: vi.fn(),
};

// Mock Mapbox GL JS module
vi.mock('mapbox-gl', () => ({
  default: mockMapboxGL,
  ...mockMapboxGL,
}));
