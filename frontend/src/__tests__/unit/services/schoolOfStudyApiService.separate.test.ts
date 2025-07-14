import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { SchoolOfStudyApiService } from '../../../js/services/schoolOfStudyApiService';
import { ApiService } from '../../../js/api';
import {
  mockSchoolOfStudyIdsResponse,
  mockSchoolOfStudyGeoJSONResponse,
} from '../../fixtures/apiResponses';

// Mock the ApiService
vi.mock('../../../js/api');

describe('SchoolOfStudyApiService', () => {
  let schoolApiService: SchoolOfStudyApiService;
  let mockApiService: any;

  beforeEach(() => {
    // Create a mock instance of ApiService
    mockApiService = {
      getSchoolOfStudyIds: vi.fn(),
      getSchoolOfStudyData: vi.fn(),
      getSchoolOfStudyExportUrl: vi.fn(),
      createAbortController: vi.fn(),
      cancelRequest: vi.fn(),
    } as any;

    // Mock the ApiService constructor to return our mock
    vi.mocked(ApiService).mockImplementation(() => mockApiService);

    schoolApiService = new SchoolOfStudyApiService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should create an instance with ApiService dependency', () => {
      expect(schoolApiService).toBeInstanceOf(SchoolOfStudyApiService);
      expect(ApiService).toHaveBeenCalledOnce();
    });
  });

  describe('getSchoolOfStudyIds', () => {
    it('should fetch school of study IDs successfully', async () => {
      const mockSignal = new AbortController().signal;
      mockApiService.getSchoolOfStudyIds.mockResolvedValue(mockSchoolOfStudyIdsResponse);

      const result = await schoolApiService.getSchoolOfStudyIds(mockSignal);

      expect(mockApiService.getSchoolOfStudyIds).toHaveBeenCalledWith(mockSignal);
      expect(result).toEqual(mockSchoolOfStudyIdsResponse);
    });

    it('should handle errors when fetching school IDs', async () => {
      const mockError = new Error('Network error');
      mockApiService.getSchoolOfStudyIds.mockRejectedValue(mockError);

      await expect(schoolApiService.getSchoolOfStudyIds()).rejects.toThrow('Network error');
    });

    it('should work without signal parameter', async () => {
      mockApiService.getSchoolOfStudyIds.mockResolvedValue(mockSchoolOfStudyIdsResponse);

      const result = await schoolApiService.getSchoolOfStudyIds();

      expect(mockApiService.getSchoolOfStudyIds).toHaveBeenCalledWith(undefined);
      expect(result).toEqual(mockSchoolOfStudyIdsResponse);
    });

    it('should validate response structure', async () => {
      const invalidResponse = { invalid: 'structure' } as any;
      mockApiService.getSchoolOfStudyIds.mockResolvedValue(invalidResponse);

      await expect(schoolApiService.getSchoolOfStudyIds()).rejects.toThrow(
        'Invalid school of study IDs response: missing school_ids array'
      );
    });

    it('should validate school_ids is an array', async () => {
      const invalidResponse = { school_ids: 'not-an-array' } as any;
      mockApiService.getSchoolOfStudyIds.mockResolvedValue(invalidResponse);

      await expect(schoolApiService.getSchoolOfStudyIds()).rejects.toThrow(
        'Invalid school of study IDs response: school_ids must be an array'
      );
    });
  });

  describe('getSchoolOfStudyData', () => {
    const testCategoryCode = 'BHGT';

    it('should fetch school of study data successfully', async () => {
      const mockSignal = new AbortController().signal;
      mockApiService.getSchoolOfStudyData.mockResolvedValue(mockSchoolOfStudyGeoJSONResponse);

      const result = await schoolApiService.getSchoolOfStudyData(testCategoryCode, mockSignal);

      expect(mockApiService.getSchoolOfStudyData).toHaveBeenCalledWith(
        testCategoryCode,
        mockSignal
      );
      expect(result).toEqual(mockSchoolOfStudyGeoJSONResponse);
    });

    it('should validate category code parameter', async () => {
      await expect(schoolApiService.getSchoolOfStudyData('')).rejects.toThrow(
        'Category code is required'
      );

      await expect(schoolApiService.getSchoolOfStudyData('   ')).rejects.toThrow(
        'Category code is required'
      );

      await expect(schoolApiService.getSchoolOfStudyData(null as any)).rejects.toThrow(
        'Category code is required'
      );
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Failed to fetch');
      mockApiService.getSchoolOfStudyData.mockRejectedValue(networkError);

      await expect(schoolApiService.getSchoolOfStudyData(testCategoryCode)).rejects.toThrow(
        'Failed to fetch'
      );
    });

    it('should validate GeoJSON response structure', async () => {
      const invalidGeoJSON = { invalid: 'structure' } as any;
      mockApiService.getSchoolOfStudyData.mockResolvedValue(invalidGeoJSON);

      await expect(schoolApiService.getSchoolOfStudyData(testCategoryCode)).rejects.toThrow(
        'Invalid GeoJSON response: missing type property'
      );
    });

    it('should validate GeoJSON type is FeatureCollection', async () => {
      const invalidGeoJSON = { type: 'Feature' } as any;
      mockApiService.getSchoolOfStudyData.mockResolvedValue(invalidGeoJSON);

      await expect(schoolApiService.getSchoolOfStudyData(testCategoryCode)).rejects.toThrow(
        'Invalid GeoJSON response: type must be FeatureCollection'
      );
    });

    it('should validate features array exists', async () => {
      const invalidGeoJSON = { type: 'FeatureCollection' } as any;
      mockApiService.getSchoolOfStudyData.mockResolvedValue(invalidGeoJSON);

      await expect(schoolApiService.getSchoolOfStudyData(testCategoryCode)).rejects.toThrow(
        'Invalid GeoJSON response: missing features array'
      );
    });

    it('should accept empty features array', async () => {
      const emptyGeoJSON = { type: 'FeatureCollection', features: [] };
      mockApiService.getSchoolOfStudyData.mockResolvedValue(emptyGeoJSON);

      const result = await schoolApiService.getSchoolOfStudyData(testCategoryCode);
      expect(result).toEqual(emptyGeoJSON);
    });
  });

  describe('getExportUrl', () => {
    const testCategoryCode = 'ETMS';

    it('should generate export URL successfully', () => {
      const expectedUrl = 'http://localhost:8000/school_of_study_data/ETMS';
      mockApiService.getSchoolOfStudyExportUrl.mockReturnValue(expectedUrl);

      const result = schoolApiService.getExportUrl(testCategoryCode);

      expect(mockApiService.getSchoolOfStudyExportUrl).toHaveBeenCalledWith(testCategoryCode);
      expect(result).toBe(expectedUrl);
    });

    it('should validate category code parameter', () => {
      expect(() => schoolApiService.getExportUrl('')).toThrow('Category code is required');
      expect(() => schoolApiService.getExportUrl('   ')).toThrow('Category code is required');
      expect(() => schoolApiService.getExportUrl(null as any)).toThrow('Category code is required');
    });

    it('should handle different category codes', () => {
      const testCases = ['BHGT', 'CAED', 'CE', 'EDU', 'ETMS', 'HS', 'LPS', 'MIT'];

      testCases.forEach((categoryCode) => {
        const expectedUrl = `http://localhost:8000/school_of_study_data/${categoryCode}`;
        mockApiService.getSchoolOfStudyExportUrl.mockReturnValue(expectedUrl);

        const result = schoolApiService.getExportUrl(categoryCode);
        expect(result).toBe(expectedUrl);
      });
    });
  });

  describe('createAbortController', () => {
    it('should create abort controller with name', () => {
      const mockController = new AbortController();
      mockApiService.createAbortController.mockReturnValue(mockController);

      const result = schoolApiService.createAbortController('test-operation');

      expect(mockApiService.createAbortController).toHaveBeenCalledWith('test-operation');
      expect(result).toBe(mockController);
    });

    it('should handle different operation names', () => {
      const testNames = ['school-ids', 'school-data', 'export-operation'];

      testNames.forEach((name) => {
        const mockController = new AbortController();
        mockApiService.createAbortController.mockReturnValue(mockController);

        const result = schoolApiService.createAbortController(name);
        expect(result).toBe(mockController);
      });
    });
  });

  describe('cancelRequest', () => {
    it('should cancel named request successfully', () => {
      mockApiService.cancelRequest.mockReturnValue(true);

      const result = schoolApiService.cancelRequest('test-operation');

      expect(mockApiService.cancelRequest).toHaveBeenCalledWith('test-operation');
      expect(result).toBe(true);
    });

    it('should return false when request does not exist', () => {
      mockApiService.cancelRequest.mockReturnValue(false);

      const result = schoolApiService.cancelRequest('non-existent');

      expect(result).toBe(false);
    });
  });

  describe('integration with real ApiService', () => {
    it('should work with actual ApiService instance', () => {
      // This test ensures our service works with the real ApiService
      vi.mocked(ApiService).mockRestore();

      const realService = new SchoolOfStudyApiService();
      expect(realService).toBeInstanceOf(SchoolOfStudyApiService);
    });
  });

  describe('error handling', () => {
    it('should preserve original error messages', async () => {
      const originalError = new Error('Original API error');
      mockApiService.getSchoolOfStudyIds.mockRejectedValue(originalError);

      await expect(schoolApiService.getSchoolOfStudyIds()).rejects.toThrow('Original API error');
    });

    it('should handle AbortError correctly', async () => {
      const abortError = new DOMException('The operation was aborted', 'AbortError');
      mockApiService.getSchoolOfStudyData.mockRejectedValue(abortError);

      await expect(schoolApiService.getSchoolOfStudyData('BHGT')).rejects.toThrow(abortError);
    });
  });

  describe('type safety', () => {
    it('should return correctly typed responses', async () => {
      mockApiService.getSchoolOfStudyIds.mockResolvedValue(mockSchoolOfStudyIdsResponse);
      mockApiService.getSchoolOfStudyData.mockResolvedValue(mockSchoolOfStudyGeoJSONResponse);

      const idsResult = await schoolApiService.getSchoolOfStudyIds();
      const dataResult = await schoolApiService.getSchoolOfStudyData('BHGT');

      // TypeScript compilation ensures these are properly typed
      expect(idsResult.school_ids).toBeInstanceOf(Array);
      expect(dataResult.type).toBe('FeatureCollection');
      expect(dataResult.features).toBeInstanceOf(Array);
    });
  });
});
