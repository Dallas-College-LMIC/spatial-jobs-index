import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useOccupationStore } from '../occupation';

// Mock the API service
vi.mock('../../../js/api', () => ({
  ApiService: vi.fn().mockImplementation(() => ({
    getOccupationIds: vi.fn(),
    getOccupationData: vi.fn(),
    createAbortController: vi.fn(() => new AbortController()),
  })),
}));

describe('Occupation Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should initialize with default state', () => {
    const store = useOccupationStore();

    expect(store.occupations).toEqual([]);
    expect(store.selectedOccupationId).toBeNull();
    expect(store.occupationData).toBeNull();
    expect(store.isLoading).toBe(false);
    expect(store.error).toBeNull();
    expect(store.searchQuery).toBe('');
    expect(store.filterOptions).toEqual({});
  });

  it('should update selected occupation', () => {
    const store = useOccupationStore();

    store.setSelectedOccupation('11-1011');
    expect(store.selectedOccupationId).toBe('11-1011');
  });

  it('should update search query', () => {
    const store = useOccupationStore();

    store.setSearchQuery('manager');
    expect(store.searchQuery).toBe('manager');
  });

  it('should update filter options', () => {
    const store = useOccupationStore();
    const filters = { category: 'management', minWage: 50000 };

    store.setFilterOptions(filters);
    expect(store.filterOptions).toEqual(filters);
  });

  it('should filter occupations by search query', () => {
    const store = useOccupationStore();
    store.occupations = [
      { code: '11-1011', name: 'Chief Executives' },
      { code: '11-1021', name: 'General and Operations Managers' },
      { code: '15-1252', name: 'Software Developers' },
    ];

    store.setSearchQuery('manager');
    const filtered = store.filteredOccupations;

    expect(filtered).toHaveLength(1);
    expect(filtered[0].name).toBe('General and Operations Managers');
  });

  it('should fetch occupation IDs', async () => {
    const store = useOccupationStore();

    // Mock the API module
    const { ApiService } = await import('../../../js/api');
    const mockGetOccupationIds = vi.fn().mockResolvedValue({
      occupations: [
        { code: '11-1011', name: 'Chief Executives' },
        { code: '11-1021', name: 'General and Operations Managers' },
      ],
    });

    (ApiService as any).mockImplementation(() => ({
      getOccupationIds: mockGetOccupationIds,
    }));

    await store.fetchOccupationIds();

    expect(mockGetOccupationIds).toHaveBeenCalled();
    expect(store.occupations).toEqual([
      { code: '11-1011', name: 'Chief Executives' },
      { code: '11-1021', name: 'General and Operations Managers' },
    ]);
  });

  it('should handle fetch occupation IDs error', async () => {
    const store = useOccupationStore();

    const { ApiService } = await import('../../../js/api');
    const mockGetOccupationIds = vi.fn().mockRejectedValue(new Error('Network error'));

    (ApiService as any).mockImplementation(() => ({
      getOccupationIds: mockGetOccupationIds,
    }));

    await store.fetchOccupationIds();

    expect(store.error).toBe('Failed to load occupations: Network error');
  });

  it('should set loading state during fetch', async () => {
    const store = useOccupationStore();

    const { ApiService } = await import('../../../js/api');

    let resolvePromise: (value: any) => void;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    const mockGetOccupationIds = vi.fn().mockReturnValue(promise);

    (ApiService as any).mockImplementation(() => ({
      getOccupationIds: mockGetOccupationIds,
    }));

    // Start fetch
    const fetchPromise = store.fetchOccupationIds();

    // Should be loading
    expect(store.isLoading).toBe(true);

    // Resolve the promise
    resolvePromise({ occupations: [] });
    await fetchPromise;

    // Should not be loading anymore
    expect(store.isLoading).toBe(false);
  });

  it('should fetch occupation data', async () => {
    const store = useOccupationStore();
    const mockGeoJSON = {
      type: 'FeatureCollection' as const,
      features: [],
    };

    const { ApiService } = await import('../../../js/api');
    const mockGetOccupationData = vi.fn().mockResolvedValue(mockGeoJSON);

    (ApiService as any).mockImplementation(() => ({
      getOccupationData: mockGetOccupationData,
      createAbortController: vi.fn(() => new AbortController()),
    }));

    await store.fetchOccupationData('11-1011');

    expect(mockGetOccupationData).toHaveBeenCalledWith('11-1011', expect.any(AbortSignal));
    expect(store.occupationData).toEqual(mockGeoJSON);
    expect(store.selectedOccupationId).toBe('11-1011');
  });

  it('should use cached data when available', async () => {
    const store = useOccupationStore();
    const mockGeoJSON = {
      type: 'FeatureCollection' as const,
      features: [],
    };

    const { ApiService } = await import('../../../js/api');
    const mockGetOccupationData = vi.fn().mockResolvedValue(mockGeoJSON);

    (ApiService as any).mockImplementation(() => ({
      getOccupationData: mockGetOccupationData,
      createAbortController: vi.fn(() => new AbortController()),
    }));

    // First fetch - should call API
    await store.fetchOccupationData('11-1012'); // Use different ID to avoid cache from previous test
    expect(mockGetOccupationData).toHaveBeenCalledTimes(1);

    // Second fetch - should use cache
    await store.fetchOccupationData('11-1012');
    expect(mockGetOccupationData).toHaveBeenCalledTimes(1); // Still only called once
    expect(store.occupationData).toEqual(mockGeoJSON);
  });
});
