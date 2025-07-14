import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { SchoolOfStudyCacheService } from '../../../js/services/schoolOfStudyCacheService';
import { createCacheService } from '../../../js/services/cacheService';
import { mockSchoolOfStudyIdsResponse } from '../../fixtures/apiResponses';

// Mock the cacheService
vi.mock('../../../js/services/cacheService');

describe('SchoolOfStudyCacheService', () => {
  let cacheService: SchoolOfStudyCacheService;
  let mockCacheService: any;

  beforeEach(() => {
    // Create a mock cache service
    mockCacheService = {
      get: vi.fn(),
      set: vi.fn(),
      remove: vi.fn(),
      clear: vi.fn(),
    };

    // Mock the createCacheService function to return our mock
    vi.mocked(createCacheService).mockReturnValue(mockCacheService);

    cacheService = new SchoolOfStudyCacheService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should create an instance with cache service dependency', () => {
      expect(cacheService).toBeInstanceOf(SchoolOfStudyCacheService);
      expect(createCacheService).toHaveBeenCalledWith('localStorage', 'sji_webapp');
    });

    it('should use correct cache configuration', () => {
      expect(createCacheService).toHaveBeenCalledWith('localStorage', 'sji_webapp');
    });
  });

  describe('getSchoolIds', () => {
    it('should return cached school IDs when available', () => {
      const cachedIds = ['BHGT', 'CAED', 'CE'];
      mockCacheService.get.mockReturnValue(cachedIds);

      const result = cacheService.getSchoolIds();

      expect(mockCacheService.get).toHaveBeenCalledWith('school_of_study_ids');
      expect(result).toBe(cachedIds);
    });

    it('should return null when no cache exists', () => {
      mockCacheService.get.mockReturnValue(null);

      const result = cacheService.getSchoolIds();

      expect(result).toBeNull();
    });

    it('should return null when cache returns undefined', () => {
      mockCacheService.get.mockReturnValue(undefined);

      const result = cacheService.getSchoolIds();

      expect(result).toBeNull();
    });

    it('should validate cached data is an array', () => {
      mockCacheService.get.mockReturnValue('invalid-data');

      const result = cacheService.getSchoolIds();

      expect(result).toBeNull();
    });

    it('should validate cached array contains only strings', () => {
      mockCacheService.get.mockReturnValue(['BHGT', 123, 'CE']);

      const result = cacheService.getSchoolIds();

      expect(result).toBeNull();
    });

    it('should accept empty array as valid cache', () => {
      mockCacheService.get.mockReturnValue([]);

      const result = cacheService.getSchoolIds();

      expect(result).toEqual([]);
    });
  });

  describe('setSchoolIds', () => {
    const defaultTTL = 24 * 60 * 60; // 24 hours

    it('should cache school IDs with default TTL', () => {
      const schoolIds = ['BHGT', 'CAED', 'CE'];

      cacheService.setSchoolIds(schoolIds);

      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        schoolIds,
        defaultTTL
      );
    });

    it('should cache school IDs with custom TTL', () => {
      const schoolIds = ['BHGT', 'CAED'];
      const customTTL = 3600; // 1 hour

      cacheService.setSchoolIds(schoolIds, customTTL);

      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        schoolIds,
        customTTL
      );
    });

    it('should validate input is an array', () => {
      expect(() => cacheService.setSchoolIds('invalid' as any)).toThrow(
        'School IDs must be an array'
      );
    });

    it('should validate array contains only strings', () => {
      expect(() => cacheService.setSchoolIds(['BHGT', 123] as any)).toThrow(
        'All school IDs must be strings'
      );
    });

    it('should validate TTL is a positive number', () => {
      expect(() => cacheService.setSchoolIds(['BHGT'], -1)).toThrow(
        'TTL must be a positive number'
      );

      expect(() => cacheService.setSchoolIds(['BHGT'], 0)).toThrow('TTL must be a positive number');
    });

    it('should accept empty array as valid input', () => {
      expect(() => cacheService.setSchoolIds([])).not.toThrow();
      expect(mockCacheService.set).toHaveBeenCalledWith('school_of_study_ids', [], defaultTTL);
    });
  });

  describe('cacheSchoolIdsResponse', () => {
    it('should extract and cache school_ids from response', () => {
      cacheService.cacheSchoolIdsResponse(mockSchoolOfStudyIdsResponse);

      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        mockSchoolOfStudyIdsResponse.school_ids,
        24 * 60 * 60
      );
    });

    it('should use custom TTL when provided', () => {
      const customTTL = 7200; // 2 hours

      cacheService.cacheSchoolIdsResponse(mockSchoolOfStudyIdsResponse, customTTL);

      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        mockSchoolOfStudyIdsResponse.school_ids,
        customTTL
      );
    });

    it('should validate response structure', () => {
      const invalidResponse = { invalid: 'structure' } as any;

      expect(() => cacheService.cacheSchoolIdsResponse(invalidResponse)).toThrow(
        'Invalid response: missing school_ids property'
      );
    });

    it('should validate school_ids is an array', () => {
      const invalidResponse = { school_ids: 'not-array' } as any;

      expect(() => cacheService.cacheSchoolIdsResponse(invalidResponse)).toThrow(
        'Invalid response: school_ids must be an array'
      );
    });
  });

  describe('hasSchoolIds', () => {
    it('should return true when valid cache exists', () => {
      mockCacheService.get.mockReturnValue(['BHGT', 'CAED']);

      const result = cacheService.hasSchoolIds();

      expect(result).toBe(true);
    });

    it('should return false when no cache exists', () => {
      mockCacheService.get.mockReturnValue(null);

      const result = cacheService.hasSchoolIds();

      expect(result).toBe(false);
    });

    it('should return false when cache contains invalid data', () => {
      mockCacheService.get.mockReturnValue('invalid-data');

      const result = cacheService.hasSchoolIds();

      expect(result).toBe(false);
    });
  });

  describe('clearSchoolIds', () => {
    it('should remove school IDs from cache', () => {
      cacheService.clearSchoolIds();

      expect(mockCacheService.remove).toHaveBeenCalledWith('school_of_study_ids');
    });
  });

  describe('clearAllCaches', () => {
    it('should clear all cache data', () => {
      cacheService.clearAllCaches();

      expect(mockCacheService.clear).toHaveBeenCalledOnce();
    });
  });

  describe('getCacheStats', () => {
    it('should return comprehensive cache statistics', () => {
      const mockIds = ['BHGT', 'CAED', 'CE'];
      mockCacheService.get.mockReturnValue(mockIds);

      const stats = cacheService.getCacheStats();

      expect(stats).toEqual({
        schoolIds: {
          exists: true,
          data: mockIds,
          isValid: true,
        },
      });
    });

    it('should handle missing cache data', () => {
      mockCacheService.get.mockReturnValue(null);

      const stats = cacheService.getCacheStats();

      expect(stats).toEqual({
        schoolIds: {
          exists: false,
          data: null,
          isValid: false,
        },
      });
    });

    it('should detect invalid cached data', () => {
      const invalidData = 'not-an-array';
      mockCacheService.get.mockReturnValue(invalidData);

      const stats = cacheService.getCacheStats();

      expect(stats.schoolIds.isValid).toBe(false);
    });
  });

  describe('integration with different cache backends', () => {
    it('should work with localStorage backend', () => {
      new SchoolOfStudyCacheService('localStorage');

      expect(createCacheService).toHaveBeenCalledWith('localStorage', 'sji_webapp');
    });

    it('should work with memory backend', () => {
      new SchoolOfStudyCacheService('memory');

      expect(createCacheService).toHaveBeenCalledWith('memory', 'sji_webapp');
    });

    it('should default to localStorage', () => {
      new SchoolOfStudyCacheService();

      expect(createCacheService).toHaveBeenCalledWith('localStorage', 'sji_webapp');
    });
  });

  describe('error handling', () => {
    it('should handle cache service errors gracefully', () => {
      mockCacheService.get.mockImplementation(() => {
        throw new Error('Cache error');
      });

      const result = cacheService.getSchoolIds();

      expect(result).toBeNull();
    });

    it('should handle set operation errors', () => {
      mockCacheService.set.mockImplementation(() => {
        throw new Error('Cache write error');
      });

      expect(() => cacheService.setSchoolIds(['BHGT'])).toThrow('Cache write error');
    });
  });

  describe('performance considerations', () => {
    it('should not modify original data when caching', () => {
      const originalIds = ['BHGT', 'CAED'];
      const copyIds = [...originalIds];

      cacheService.setSchoolIds(originalIds);

      expect(originalIds).toEqual(copyIds); // Should remain unchanged
    });

    it('should handle large datasets efficiently', () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => `SCHOOL_${i}`);

      expect(() => cacheService.setSchoolIds(largeDataset)).not.toThrow();
      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        largeDataset,
        24 * 60 * 60
      );
    });
  });

  describe('TTL management', () => {
    it('should use class constant for default TTL', () => {
      const schoolIds = ['BHGT'];
      cacheService.setSchoolIds(schoolIds);

      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        schoolIds,
        24 * 60 * 60 // 24 hours
      );
    });

    it('should accept different TTL units', () => {
      const schoolIds = ['BHGT'];
      const oneMinute = 60;
      const oneHour = 60 * 60;
      const oneDay = 24 * 60 * 60;

      cacheService.setSchoolIds(schoolIds, oneMinute);
      expect(mockCacheService.set).toHaveBeenCalledWith(
        'school_of_study_ids',
        schoolIds,
        oneMinute
      );

      cacheService.setSchoolIds(schoolIds, oneHour);
      expect(mockCacheService.set).toHaveBeenCalledWith('school_of_study_ids', schoolIds, oneHour);

      cacheService.setSchoolIds(schoolIds, oneDay);
      expect(mockCacheService.set).toHaveBeenCalledWith('school_of_study_ids', schoolIds, oneDay);
    });
  });
});
