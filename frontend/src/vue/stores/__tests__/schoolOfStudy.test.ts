import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useSchoolOfStudyStore } from '../schoolOfStudy';

// Mock the API service
vi.mock('../../../js/api', () => ({
  ApiService: vi.fn().mockImplementation(() => ({
    getSchoolOfStudyIds: vi.fn(),
    getSchoolOfStudyData: vi.fn(),
    createAbortController: vi.fn(() => new AbortController()),
  })),
}));

describe('School of Study Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should initialize with default state', () => {
    const store = useSchoolOfStudyStore();

    expect(store.schoolIds).toEqual([]);
    expect(store.selectedSchoolId).toBeNull();
    expect(store.schoolData).toBeNull();
    expect(store.isLoading).toBe(false);
    expect(store.error).toBeNull();
    expect(store.searchQuery).toBe('');
  });

  it('should fetch school of study IDs', async () => {
    const store = useSchoolOfStudyStore();

    const { ApiService } = await import('../../../js/api');
    const mockGetSchoolOfStudyIds = vi.fn().mockResolvedValue({
      school_ids: ['01.0101', '01.0102', '01.0103'],
    });

    (ApiService as any).mockImplementation(() => ({
      getSchoolOfStudyIds: mockGetSchoolOfStudyIds,
    }));

    await store.fetchSchoolIds();

    expect(mockGetSchoolOfStudyIds).toHaveBeenCalled();
    expect(store.schoolIds).toEqual(['01.0101', '01.0102', '01.0103']);
  });

  it('should fetch school of study data', async () => {
    const store = useSchoolOfStudyStore();
    const mockGeoJSON = {
      type: 'FeatureCollection' as const,
      features: [],
    };

    const { ApiService } = await import('../../../js/api');
    const mockGetSchoolOfStudyData = vi.fn().mockResolvedValue(mockGeoJSON);

    (ApiService as any).mockImplementation(() => ({
      getSchoolOfStudyData: mockGetSchoolOfStudyData,
      createAbortController: vi.fn(() => new AbortController()),
    }));

    await store.fetchSchoolData('01.0101');

    expect(mockGetSchoolOfStudyData).toHaveBeenCalledWith('01.0101', expect.any(AbortSignal));
    expect(store.schoolData).toEqual(mockGeoJSON);
    expect(store.selectedSchoolId).toBe('01.0101');
  });
});
