/**
 * Tests for API type safety improvements
 */
import { describe, it, expect } from 'vitest';
import type { IsochroneResponse } from '../../../types/api';

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
});
