/**
 * Tests for API type safety improvements
 */
import { describe, it, expect } from 'vitest';
import type { IsochroneResponse, ApiError } from '../../../types/api';

describe('API Type Safety', () => {
  it('should use IsochroneResponse type for proper type safety', () => {
    // This test requires IsochroneResponse type to be defined
    const validIsochroneData: IsochroneResponse = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: { type: 'Polygon', coordinates: [] },
          properties: { geoid: '12345', travel_time_minutes: 30 },
        },
      ],
    };

    expect(validIsochroneData.type).toBe('FeatureCollection');
    expect(Array.isArray(validIsochroneData.features)).toBe(true);

    // Test the first feature properties with proper null checking
    const firstFeature = validIsochroneData.features[0];
    expect(firstFeature).toBeDefined();
    expect(firstFeature?.properties.geoid).toBe('12345');
    expect(firstFeature?.properties.travel_time_minutes).toBe(30);
  });

  it('should use proper coordinate types for geometry', () => {
    // This test verifies that IsochroneFeature geometry uses proper types
    const feature: IsochroneResponse['features'][0] = {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        // This should be properly typed, not 'any'
        coordinates: [
          [
            [-96.75, 32.75],
            [-96.74, 32.76],
            [-96.73, 32.75],
            [-96.75, 32.75],
          ],
        ],
      },
      properties: { geoid: '12345', travel_time_minutes: 30 },
    };

    // Verify the coordinates are properly typed
    const coords = feature.geometry.coordinates;
    expect(Array.isArray(coords)).toBe(true);

    // This should work with proper typing (accessing nested array elements)
    if (feature.geometry.type === 'Polygon') {
      const firstRing = coords[0];
      expect(Array.isArray(firstRing)).toBe(true);
      const firstPoint = firstRing?.[0];
      expect(Array.isArray(firstPoint)).toBe(true);
      expect(typeof firstPoint?.[0]).toBe('number'); // longitude
      expect(typeof firstPoint?.[1]).toBe('number'); // latitude
    }
  });

  it('should have proper ApiError type for enhanced error handling', () => {
    // This test requires ApiError type to be defined
    const apiError: ApiError = new Error('Test error') as ApiError;
    apiError.status = 404;
    apiError.statusText = 'Not Found';
    apiError.body = 'Resource not found';
    apiError.endpoint = '/api/test';
    apiError.url = 'http://localhost:8000/api/test';

    expect(apiError.status).toBe(404);
    expect(apiError.statusText).toBe('Not Found');
    expect(apiError.body).toBe('Resource not found');
    expect(apiError.endpoint).toBe('/api/test');
    expect(apiError.url).toBe('http://localhost:8000/api/test');
  });
});
