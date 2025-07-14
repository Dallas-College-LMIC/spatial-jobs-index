import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { ApiService } from '../../../js/api';
import { createFetchResponse } from '../../utils/testHelpers';
import {
  mockSchoolOfStudyIdsResponse,
  mockSchoolOfStudyGeoJSONResponse,
} from '../../fixtures/apiResponses';

describe('SchoolOfStudyApiService', () => {
  let apiService: ApiService;

  beforeEach(() => {
    apiService = new ApiService();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getSchoolOfStudyIds', () => {
    it('should fetch school of study IDs successfully', async () => {
      const mockResponse = createFetchResponse(mockSchoolOfStudyIdsResponse);
      vi.mocked(global.fetch).mockResolvedValueOnce(mockResponse);

      const result = await apiService.getSchoolOfStudyIds();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/school_of_study_ids'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          signal: expect.any(AbortSignal),
        })
      );
      expect(result).toEqual(mockSchoolOfStudyIdsResponse);
    });
  });

  describe('getSchoolOfStudyData', () => {
    it('should fetch school of study data successfully', async () => {
      const categoryCode = 'BHGT';
      const mockResponse = createFetchResponse(mockSchoolOfStudyGeoJSONResponse);
      vi.mocked(global.fetch).mockResolvedValueOnce(mockResponse);

      const result = await apiService.getSchoolOfStudyData(categoryCode);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/school_of_study_data/${categoryCode}`),
        expect.objectContaining({
          method: 'GET',
          signal: expect.any(AbortSignal),
        })
      );
      expect(result).toEqual(mockSchoolOfStudyGeoJSONResponse);
    });
  });

  describe('getSchoolOfStudyExportUrl', () => {
    it('should generate correct export URL for school category', () => {
      const categoryCode = 'BHGT';
      const expectedUrl = `http://localhost:8000/school_of_study_data/${categoryCode}`;

      const exportUrl = apiService.getSchoolOfStudyExportUrl(categoryCode);

      expect(exportUrl).toBe(expectedUrl);
    });
  });
});
