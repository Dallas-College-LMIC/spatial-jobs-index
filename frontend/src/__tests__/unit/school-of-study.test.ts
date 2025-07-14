import { describe, it, expect, beforeEach, vi } from 'vitest';
import '../mocks/mapbox-gl';
import '../mocks/jquery';

// Mock all dependencies before importing
vi.mock('../../js/services/schoolOfStudyApiService');
vi.mock('../../js/services/schoolOfStudyCacheService');
vi.mock('../../js/services/uiService');
vi.mock('../../js/utils/errorHandler');
vi.mock('../../js/controllers/baseMapController');
vi.mock('../../js/mapUtils');

// Import after mocking
import { SchoolOfStudyMapController } from '../../js/school-of-study';

describe('SchoolOfStudyMapController', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Setup basic DOM
    document.body.innerHTML = `
      <div id="test-container"></div>
      <div id="loading"></div>
      <select id="school-select">
        <option value="">Select a school of study...</option>
      </select>
      <a id="exp"></a>
    `;

    // Mock jQuery
    (global as any).$ = vi.fn().mockReturnValue({
      select2: vi.fn().mockReturnThis(),
      on: vi.fn().mockReturnThis(),
      val: vi.fn().mockReturnThis(),
      trigger: vi.fn().mockReturnThis(),
    });
  });

  describe('constructor', () => {
    it('should create instance successfully', () => {
      expect(() => {
        new SchoolOfStudyMapController('test-container');
      }).not.toThrow();
    });
  });

  describe('getSchoolDisplayName', () => {
    it('should return display name for known school codes', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('BHGT');
      expect(displayName).toBe('Business, Hospitality, and Graphic Technology');
    });

    it('should return display name for CAED', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('CAED');
      expect(displayName).toBe('Career and Educational Development');
    });

    it('should return display name for CE', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('CE');
      expect(displayName).toBe('Continuing Education');
    });

    it('should return display name for EDU', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('EDU');
      expect(displayName).toBe('Education');
    });

    it('should return display name for ETMS', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('ETMS');
      expect(displayName).toBe('Electronics, Technology, Mathematics, and Science');
    });

    it('should return display name for HS', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('HS');
      expect(displayName).toBe('Health Sciences');
    });

    it('should return display name for LPS', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('LPS');
      expect(displayName).toBe('Liberal and Professional Studies');
    });

    it('should return display name for MIT', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('MIT');
      expect(displayName).toBe('Manufacturing, Industrial Technology');
    });

    it('should return school code for unknown codes', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      const displayName = (controller as any).getSchoolDisplayName('UNKNOWN');
      expect(displayName).toBe('UNKNOWN');
    });
  });

  describe('getLayerIds', () => {
    it('should return school layer when school is selected', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      (controller as any).currentSchoolId = 'BHGT';

      const layerIds = (controller as any).getLayerIds();
      expect(layerIds).toEqual(['school-layer']);
    });

    it('should return empty array when no school selected', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      (controller as any).currentSchoolId = null;

      const layerIds = (controller as any).getLayerIds();
      expect(layerIds).toEqual([]);
    });
  });

  describe('cache management', () => {
    it('should have clearAllCaches method', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      expect(typeof controller.clearAllCaches).toBe('function');
    });

    it('should have getCacheStats method', () => {
      const controller = new SchoolOfStudyMapController('test-container');
      expect(typeof controller.getCacheStats).toBe('function');
    });
  });

  describe('updateExportLink', () => {
    it('should handle missing export button', () => {
      document.getElementById('exp')?.remove();
      const controller = new SchoolOfStudyMapController('test-container');

      // Should not throw error
      expect(() => (controller as any).updateExportLink()).not.toThrow();
    });
  });
});
