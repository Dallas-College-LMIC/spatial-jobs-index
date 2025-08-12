import { describe, it, expect } from 'vitest';
import { useMapbox } from '../../composables/useMapbox';

describe('useMapbox composable', () => {
  it('should return mapbox configuration', () => {
    const { getMapboxToken } = useMapbox();
    expect(getMapboxToken).toBeDefined();
    expect(typeof getMapboxToken).toBe('function');
  });
});
