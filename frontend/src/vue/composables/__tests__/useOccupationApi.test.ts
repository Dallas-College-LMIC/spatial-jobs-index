import { describe, it, expect } from 'vitest';
import { useOccupationApi } from '../useOccupationApi';

describe('useOccupationApi', () => {
  it('should provide fetchOccupationIds function', () => {
    const { fetchOccupationIds } = useOccupationApi();
    expect(fetchOccupationIds).toBeDefined();
    expect(typeof fetchOccupationIds).toBe('function');
  });

  it('should provide occupation IDs state', () => {
    const { occupationIds, occupationIdsLoading, occupationIdsError } = useOccupationApi();
    expect(occupationIds).toBeDefined();
    expect(occupationIdsLoading).toBeDefined();
    expect(occupationIdsError).toBeDefined();
  });

  it('should provide fetchOccupationData function', () => {
    const { fetchOccupationData } = useOccupationApi();
    expect(fetchOccupationData).toBeDefined();
    expect(typeof fetchOccupationData).toBe('function');
  });
});
