import { BaseMapController } from './controllers/baseMapController';
import { SchoolOfStudyApiService } from './services/schoolOfStudyApiService';
import { SchoolOfStudyCacheService } from './services/schoolOfStudyCacheService';
import { uiService } from './services/uiService';
import { ErrorHandler } from './utils/errorHandler';

export class SchoolOfStudyMapController extends BaseMapController {
  private schoolApiService: SchoolOfStudyApiService;
  private schoolCacheService: SchoolOfStudyCacheService;
  private activeRequests = new Map<string, Promise<void>>(); // Request deduplication
  private currentSchoolId: string | null = null; // Track current school category
  private currentAbortController: AbortController | null = null; // Track current request abort controller

  constructor(containerId: string) {
    super(containerId, 'school_of_study_data');
    this.schoolApiService = new SchoolOfStudyApiService();
    this.schoolCacheService = new SchoolOfStudyCacheService();

    this.initialize().catch((error) => {
      const err = error instanceof Error ? error : new Error(String(error));
      ErrorHandler.logError(err, 'Controller Initialization', {
        controller: 'SchoolOfStudyMapController',
      });
    });
  }

  async initialize(): Promise<void> {
    // Initialize map immediately without waiting for school IDs
    await this.initializeMapWithEmptySource();

    // Load school IDs asynchronously (non-blocking)
    this.loadSchoolOfStudyIds().catch((error) => {
      const err = error instanceof Error ? error : new Error(String(error));
      ErrorHandler.logError(err, 'School of Study IDs Loading', {
        controller: 'SchoolOfStudyMapController',
      });
    });
  }

  private async loadSchoolOfStudyIds(): Promise<void> {
    this.showLoading('loading', 'Loading schools of study...');

    try {
      // Check cache first
      const cachedData = this.schoolCacheService.getSchoolIds();
      if (cachedData && cachedData.length > 0) {
        console.log('Using cached school of study IDs');
        this.populateSchoolDropdown(cachedData);
        this.hideLoading('loading');
        return;
      }

      // Create abort controller for this request
      const controller = this.schoolApiService.createAbortController('school-of-study-ids');

      // Fetch from API if not cached
      const response = await this.schoolApiService.getSchoolOfStudyIds(controller.signal);
      console.log('Loaded school of study IDs response:', response);

      // Cache the response using the cache service
      this.schoolCacheService.cacheSchoolIdsResponse(response);

      this.populateSchoolDropdown(response.school_ids);

      this.hideLoading('loading');
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));

      // Don't show error notification for abort errors
      if (err.name !== 'AbortError') {
        ErrorHandler.logError(err, 'Load School of Study IDs');
        this.showError('loading', 'Error loading schools of study');
        uiService.showNotification({
          type: 'error',
          message: 'Failed to load school of study list. Please refresh the page to try again.',
          duration: 10000,
        });
      } else {
        this.hideLoading('loading');
        console.log('[SchoolOfStudyController] School IDs loading was cancelled');
      }
    }
  }

  private populateSchoolDropdown(schoolIds: string[]): void {
    const selectElement = document.getElementById('school-select') as HTMLSelectElement;
    if (!selectElement) {
      console.error('[SchoolOfStudyController] School select element not found');
      return;
    }

    try {
      // Clear existing options except the first placeholder
      selectElement.innerHTML = '<option value="">Select a school of study...</option>';

      // Add school options
      schoolIds.forEach((schoolId) => {
        const option = document.createElement('option');
        option.value = schoolId;
        option.textContent = this.getSchoolDisplayName(schoolId);
        selectElement.appendChild(option);
      });

      // Initialize Select2 for searchable dropdown
      if (typeof (window as any).$ !== 'undefined') {
        (window as any).$('#school-select').select2({
          width: '100%',
          placeholder: 'Select a school of study...',
          allowClear: true,
        });

        // Setup change listener for Select2
        (window as any).$('#school-select').on('change', (event: any) => {
          const schoolId = event.target.value;
          if (schoolId) {
            this.loadSchoolData(schoolId);
          } else {
            this.clearMap();
          }
        });
      } else {
        // Fallback for regular select element
        selectElement.addEventListener('change', (event) => {
          const schoolId = (event.target as HTMLSelectElement).value;
          if (schoolId) {
            this.loadSchoolData(schoolId);
          } else {
            this.clearMap();
          }
        });
      }

      console.log(`[SchoolOfStudyController] Populated dropdown with ${schoolIds.length} schools`);
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      ErrorHandler.logError(err, 'Populate School Dropdown');
      this.showError('loading', 'Error setting up school dropdown');
    }
  }

  private getSchoolDisplayName(schoolId: string): string {
    // Map school codes to display names
    const displayNames: Record<string, string> = {
      BHGT: 'Business, Hospitality, and Graphic Technology',
      CAED: 'Career and Educational Development',
      CE: 'Continuing Education',
      EDU: 'Education',
      ETMS: 'Electronics, Technology, Mathematics, and Science',
      HS: 'Health Sciences',
      LPS: 'Liberal and Professional Studies',
      MIT: 'Manufacturing, Industrial Technology',
    };
    return displayNames[schoolId] || schoolId;
  }

  private async loadSchoolData(schoolId: string): Promise<void> {
    // Prevent duplicate requests
    if (this.activeRequests.has(schoolId)) {
      console.log(`[SchoolOfStudyController] Request for ${schoolId} already in progress`);
      await this.activeRequests.get(schoolId);
      return;
    }

    // Cancel any previous request
    if (this.currentAbortController) {
      this.currentAbortController.abort();
    }

    // Track current selection
    this.currentSchoolId = schoolId;
    this.currentAbortController = this.schoolApiService.createAbortController('school-data');

    const loadPromise = this.performSchoolDataLoad(schoolId);
    this.activeRequests.set(schoolId, loadPromise);

    try {
      await loadPromise;
    } finally {
      this.activeRequests.delete(schoolId);
    }
  }

  private async performSchoolDataLoad(schoolId: string): Promise<void> {
    console.log(`[SchoolOfStudyController] Loading data for school: ${schoolId}`);
    this.showLoading('loading', 'Loading school data...');

    try {
      if (!this.currentAbortController) {
        throw new Error('No abort controller available');
      }

      const geojsonData = await this.schoolApiService.getSchoolOfStudyData(
        schoolId,
        this.currentAbortController.signal
      );

      console.log(
        `[SchoolOfStudyController] Loaded ${geojsonData.features.length} features for ${schoolId}`
      );

      // Update map data
      if (this.mapManager && geojsonData.features.length > 0) {
        // Clear existing data
        this.clearMap();

        // Add the new GeoJSON data
        this.mapManager.addSource(this.sourceId, geojsonData);

        // Add or update the school layer with fixed property names
        this.addOrUpdateLayer(
          'school-layer',
          this.sourceId,
          'openings_2024_zscore_color', // Fixed property name for categories
          'visible',
          `School of Study: ${this.getSchoolDisplayName(schoolId)}`,
          'openings_2024_zscore' // Fixed property name for z-scores
        );

        // Update export link
        this.updateExportLink();

        console.log(`[SchoolOfStudyController] Map updated with data for ${schoolId}`);
      } else {
        console.warn(`[SchoolOfStudyController] No features found for ${schoolId}`);
        this.showError('loading', `No data available for ${this.getSchoolDisplayName(schoolId)}`);
      }

      this.hideLoading('loading');
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));

      if (err.name !== 'AbortError') {
        ErrorHandler.logError(err, 'Load School Data', { schoolId });
        this.showError('loading', 'Error loading school data');
        uiService.showNotification({
          type: 'error',
          message: `Failed to load data for ${this.getSchoolDisplayName(schoolId)}. Please try again.`,
          duration: 8000,
        });
      } else {
        this.hideLoading('loading');
        console.log(`[SchoolOfStudyController] Loading cancelled for ${schoolId}`);
      }
    }
  }

  protected updateExportLink(): void {
    const exportButton = document.getElementById('exp') as HTMLAnchorElement;
    if (exportButton && this.currentSchoolId) {
      exportButton.href = this.schoolApiService.getExportUrl(this.currentSchoolId);
      exportButton.style.display = 'inline-block';
    } else if (exportButton) {
      exportButton.href = '#';
      exportButton.style.display = 'none';
    }
  }

  protected getLayerIds(): string[] {
    return this.currentSchoolId ? ['school-layer'] : [];
  }

  public clearAllCaches(): void {
    this.schoolCacheService.clearAllCaches();
    console.log('[SchoolOfStudyController] All caches cleared');
  }

  public getCacheStats(): any {
    return this.schoolCacheService.getCacheStats();
  }
}
