import { createCacheService, ICacheService } from './cacheService';
import type { SchoolOfStudyIdsResponse } from '../../types/api';

/**
 * Cache service specifically for School of Study data
 * Provides high-level caching operations with validation and error handling
 */
export class SchoolOfStudyCacheService {
  private cacheService: ICacheService;
  private readonly CACHE_KEY = 'school_of_study_ids';
  private readonly DEFAULT_TTL = 24 * 60 * 60; // 24 hours in seconds

  constructor(backend: 'localStorage' | 'memory' = 'localStorage') {
    this.cacheService = createCacheService(backend, 'sji_webapp');
  }

  /**
   * Get cached school IDs with validation
   * @returns Array of school IDs or null if not cached or invalid
   */
  getSchoolIds(): string[] | null {
    try {
      const cached = this.cacheService.get<string[]>(this.CACHE_KEY);

      if (!cached) {
        return null;
      }

      // Validate cached data
      if (!Array.isArray(cached)) {
        return null;
      }

      // Validate all items are strings
      if (!cached.every((id) => typeof id === 'string')) {
        return null;
      }

      return cached;
    } catch {
      // Return null on any error to gracefully handle cache failures
      return null;
    }
  }

  /**
   * Cache school IDs with validation
   * @param schoolIds Array of school ID strings
   * @param ttl Time to live in seconds (defaults to 24 hours)
   * @throws Error if validation fails
   */
  setSchoolIds(schoolIds: string[], ttl: number = this.DEFAULT_TTL): void {
    // Validate input
    if (!Array.isArray(schoolIds)) {
      throw new Error('School IDs must be an array');
    }

    if (!schoolIds.every((id) => typeof id === 'string')) {
      throw new Error('All school IDs must be strings');
    }

    if (typeof ttl !== 'number' || ttl <= 0) {
      throw new Error('TTL must be a positive number');
    }

    this.cacheService.set(this.CACHE_KEY, schoolIds, ttl);
  }

  /**
   * Cache school IDs from API response
   * @param response The API response containing school_ids
   * @param ttl Time to live in seconds (defaults to 24 hours)
   * @throws Error if response structure is invalid
   */
  cacheSchoolIdsResponse(response: SchoolOfStudyIdsResponse, ttl: number = this.DEFAULT_TTL): void {
    // Validate response structure
    if (!response || typeof response !== 'object' || !('school_ids' in response)) {
      throw new Error('Invalid response: missing school_ids property');
    }

    if (!Array.isArray(response.school_ids)) {
      throw new Error('Invalid response: school_ids must be an array');
    }

    this.setSchoolIds(response.school_ids, ttl);
  }

  /**
   * Check if school IDs are cached
   * @returns true if school IDs exist in cache
   */
  hasSchoolIds(): boolean {
    return this.getSchoolIds() !== null;
  }

  /**
   * Remove school IDs from cache
   */
  clearSchoolIds(): void {
    this.cacheService.remove(this.CACHE_KEY);
  }

  /**
   * Clear all cached data
   */
  clearAllCaches(): void {
    this.cacheService.clear();
  }

  /**
   * Get comprehensive cache statistics
   * @returns Object containing cache statistics and validation status
   */
  getCacheStats(): {
    schoolIds: {
      exists: boolean;
      data: string[] | null;
      isValid: boolean;
    };
  } {
    const exists = this.hasSchoolIds();
    const data = this.getSchoolIds();
    const isValid = data !== null && Array.isArray(data);

    return {
      schoolIds: {
        exists,
        data,
        isValid,
      },
    };
  }
}
