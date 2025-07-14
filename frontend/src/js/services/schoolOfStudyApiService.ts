import { ApiService } from '../api';
import type { SchoolOfStudyIdsResponse, GeoJSONResponse } from '../../types/api';

/**
 * Service class for handling School of Study API operations
 * Provides a layer of abstraction over the base ApiService for school-specific operations
 */
export class SchoolOfStudyApiService {
  private apiService: ApiService;

  constructor() {
    this.apiService = new ApiService();
  }

  /**
   * Fetch all available school of study IDs
   * @param signal Optional AbortSignal for request cancellation
   * @returns Promise resolving to school of study IDs response
   * @throws Error if response is invalid or network request fails
   */
  async getSchoolOfStudyIds(signal?: AbortSignal): Promise<SchoolOfStudyIdsResponse> {
    const response = await this.apiService.getSchoolOfStudyIds(signal);

    // Validate response structure
    if (!response || typeof response !== 'object' || !('school_ids' in response)) {
      throw new Error('Invalid school of study IDs response: missing school_ids array');
    }

    if (!Array.isArray(response.school_ids)) {
      throw new Error('Invalid school of study IDs response: school_ids must be an array');
    }

    return response;
  }

  /**
   * Fetch GeoJSON data for a specific school of study category
   * @param categoryCode The school category code (e.g., 'BHGT', 'ETMS')
   * @param signal Optional AbortSignal for request cancellation
   * @returns Promise resolving to GeoJSON data
   * @throws Error if categoryCode is invalid or response is malformed
   */
  async getSchoolOfStudyData(categoryCode: string, signal?: AbortSignal): Promise<GeoJSONResponse> {
    // Validate input
    if (!categoryCode || typeof categoryCode !== 'string' || categoryCode.trim() === '') {
      throw new Error('Category code is required');
    }

    const response = await this.apiService.getSchoolOfStudyData(categoryCode.trim(), signal);

    // Validate GeoJSON structure
    if (!response || typeof response !== 'object' || !('type' in response)) {
      throw new Error('Invalid GeoJSON response: missing type property');
    }

    if (response.type !== 'FeatureCollection') {
      throw new Error('Invalid GeoJSON response: type must be FeatureCollection');
    }

    if (!Array.isArray(response.features)) {
      throw new Error('Invalid GeoJSON response: missing features array');
    }

    return response;
  }

  /**
   * Generate export URL for downloading school of study data
   * @param categoryCode The school category code
   * @returns Export URL string
   * @throws Error if categoryCode is invalid
   */
  getExportUrl(categoryCode: string): string {
    // Validate input
    if (!categoryCode || typeof categoryCode !== 'string' || categoryCode.trim() === '') {
      throw new Error('Category code is required');
    }

    return this.apiService.getSchoolOfStudyExportUrl(categoryCode.trim());
  }

  /**
   * Create a named AbortController for request management
   * @param name Unique name for the controller
   * @returns AbortController instance
   */
  createAbortController(name: string): AbortController {
    return this.apiService.createAbortController(name);
  }

  /**
   * Cancel a named request
   * @param name Name of the request to cancel
   * @returns true if request was cancelled, false if not found
   */
  cancelRequest(name: string): boolean {
    return this.apiService.cancelRequest(name);
  }
}
