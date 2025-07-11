import { ICacheService } from './cacheService';

/**
 * Occupation data structure
 */
export interface Occupation {
  code: string;
  name: string;
}

/**
 * Simple cache service for occupation data with localStorage fallback
 */
export class OccupationIdsCacheService {
  private cacheService: ICacheService;
  private readonly CACHE_KEY = 'occupation_ids';
  private readonly CACHE_TTL = 24 * 60 * 60; // 24 hours in seconds

  constructor(cacheService: ICacheService) {
    this.cacheService = cacheService;
  }

  /**
   * Cache occupations
   */
  cacheOccupations(occupations: Occupation[]): void {
    this.cacheService.set(this.CACHE_KEY, occupations, this.CACHE_TTL);
  }

  /**
   * Get cached occupations
   */
  getCachedOccupations(): Occupation[] | null {
    return this.cacheService.get<Occupation[]>(this.CACHE_KEY);
  }

  /**
   * Clear cached occupations
   */
  clearCache(): void {
    this.cacheService.remove(this.CACHE_KEY);
  }

  /**
   * Legacy method for backward compatibility - caches occupation IDs only
   * @deprecated Use cacheOccupations instead
   */
  cacheOccupationIds(occupationIds: string[]): void {
    const occupations = occupationIds.map((id) => ({ code: id, name: '' }));
    this.cacheOccupations(occupations);
  }

  /**
   * Legacy method for backward compatibility - returns occupation codes only
   * @deprecated Use getCachedOccupations instead
   */
  getCachedOccupationIds(): string[] | null {
    const occupations = this.getCachedOccupations();
    return occupations ? occupations.map((occ) => occ.code) : null;
  }
}
