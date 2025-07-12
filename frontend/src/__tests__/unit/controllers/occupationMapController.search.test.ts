import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import '../../mocks/mapbox-gl';
import '../../mocks/jquery';
import { setupOccupationControllerMocks } from '../../utils/occupationTestHelpers';
import { createMockLocalStorage } from '../../utils/testHelpers';
import { mockOccupationIdsResponse } from '../../fixtures/apiResponses';

// Setup all mocks before imports
setupOccupationControllerMocks();

// Now import the actual modules
import { OccupationMapController } from '../../../js/occupation';
import { uiService } from '../../../js/services/uiService';

describe('OccupationMapController - Search Functionality', () => {
  let controller: OccupationMapController;
  let mockLocalStorage: Storage;
  let mockApiService: any;
  let mockCacheService: any;
  let mockOccupationCache: any;
  let mockMapManager: any;
  let mockSelect2Instance: any;

  beforeEach(async () => {
    vi.clearAllMocks();

    // Setup mock localStorage
    mockLocalStorage = createMockLocalStorage();
    global.localStorage = mockLocalStorage;

    // Mock DOM Option constructor
    global.Option = vi.fn().mockImplementation((text: string, value: string) => ({
      text,
      value,
      selected: false,
      disabled: false,
    }));

    // Mock document.createElement for option elements
    const originalCreateElement = document.createElement.bind(document);
    vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      if (tagName === 'option') {
        return {
          value: '',
          text: '',
          selected: false,
          disabled: false,
        } as any;
      }
      return originalCreateElement(tagName);
    });

    // Setup mock DOM elements
    document.body.innerHTML = `
      <div id="test-container"></div>
      <div id="loading"></div>
      <select id="occupation-select">
        <option value="">Select an occupation...</option>
      </select>
      <a id="exportGeoJSON"></a>
      <a id="exp"></a>
    `;

    // Mock document.getElementById to return the proper elements
    vi.spyOn(document, 'getElementById').mockImplementation((id: string) => {
      return document.querySelector(`#${id}`) as HTMLElement | null;
    });

    // Create mock select2 instance with methods
    mockSelect2Instance = {
      select2: vi.fn().mockReturnThis(),
      on: vi.fn(),
      off: vi.fn(),
      val: vi.fn(),
      trigger: vi.fn(),
      find: vi.fn().mockReturnThis(),
      remove: vi.fn().mockReturnThis(),
      append: vi.fn().mockReturnThis(),
      length: 1,
      [0]: {} as HTMLElement,
    };

    // Mock jQuery to return our custom mock
    (global as any).$ = vi.fn().mockReturnValue(mockSelect2Instance);
    // Add jQuery utility functions
    (global as any).$.trim = vi.fn((str: string) => (str || '').trim());

    // Create controller
    controller = new OccupationMapController('test-container');

    // Get mocked services from the controller
    mockApiService = (controller as any).apiService;
    mockCacheService = (controller as any).cacheService;
    mockOccupationCache = (controller as any).occupationCache;
    mockMapManager = (controller as any).mapManager;

    // Setup service mocks
    if (!mockApiService.getOccupationIds) {
      mockApiService.getOccupationIds = vi.fn();
      mockApiService.getOccupationData = vi.fn();
      mockApiService.cancelAllRequests = vi.fn();
      mockApiService.createAbortController = vi.fn(() => new AbortController());
      mockApiService.cancelRequest = vi.fn();
      mockApiService.getAbortController = vi.fn();
    }
    if (!mockCacheService.get) {
      mockCacheService.get = vi.fn();
      mockCacheService.set = vi.fn();
      mockCacheService.remove = vi.fn();
    }
    if (!mockOccupationCache.get) {
      mockOccupationCache.get = vi.fn();
      mockOccupationCache.set = vi.fn();
      mockOccupationCache.clear = vi.fn();
      mockOccupationCache.getDebugInfo = vi.fn();
    }
    if (!mockMapManager.addSource) {
      mockMapManager.addSource = vi.fn();
    }

    // Wait for initialization
    await new Promise((resolve) => setTimeout(resolve, 10));
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('populateOccupationDropdown with new data format', () => {
    it('should populate dropdown with code and name display format', () => {
      const occupations = mockOccupationIdsResponse.occupations;

      controller['populateOccupationDropdown'](occupations);

      // Check that option elements were created
      expect(document.createElement).toHaveBeenCalledWith('option');
      expect(mockSelect2Instance.append).toHaveBeenCalledTimes(occupations.length);

      // Verify that append was called for each occupation
      const appendCalls = mockSelect2Instance.append.mock.calls;
      expect(appendCalls.length).toBe(occupations.length);

      // Check that options have correct properties set
      const firstOption = appendCalls[0][0];
      expect(firstOption.value).toBe('11-1011');
      expect(firstOption.text).toBe('11-1011 - Chief Executives');
    });

    it('should clear existing options except the placeholder', () => {
      const occupations = [{ code: '11-1011', name: 'Chief Executives' }];

      controller['populateOccupationDropdown'](occupations);

      // Verify find and remove were called correctly
      expect(mockSelect2Instance.find).toHaveBeenCalledWith('option:not(:first)');
      expect(mockSelect2Instance.remove).toHaveBeenCalled();
    });

    it('should initialize Select2 with custom matcher for code/name search', () => {
      const occupations = mockOccupationIdsResponse.occupations;

      controller['populateOccupationDropdown'](occupations);

      // Verify Select2 was initialized with correct options
      expect(mockSelect2Instance.select2).toHaveBeenCalledWith({
        placeholder: 'Search by occupation code or name...',
        allowClear: true,
        width: '100%',
        matcher: expect.any(Function),
      });
    });

    it('should show success notification with occupation count', () => {
      const occupations = mockOccupationIdsResponse.occupations;

      controller['populateOccupationDropdown'](occupations);

      expect(uiService.showNotification).toHaveBeenCalledWith({
        type: 'success',
        message: `Loaded ${occupations.length} occupations`,
        duration: 3000,
      });
    });
  });

  describe('Select2 custom matcher function', () => {
    let matcherFunction: any;

    beforeEach(() => {
      const occupations = mockOccupationIdsResponse.occupations;
      controller['populateOccupationDropdown'](occupations);

      // Extract the matcher function from the Select2 call
      const select2Call = mockSelect2Instance.select2.mock.calls[0][0];
      matcherFunction = select2Call.matcher;
    });

    it('should return all data when search term is empty', () => {
      const params = { term: '' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should return null when data has no text property', () => {
      const params = { term: 'chief' };
      const data = {}; // No text property

      const result = matcherFunction(params, data);

      expect(result).toBeNull();
    });

    it('should match occupation code (case-insensitive)', () => {
      const params = { term: '11-1011' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match occupation code with different case', () => {
      const params = { term: '11-1011' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match occupation name (case-insensitive)', () => {
      const params = { term: 'chief' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match occupation name with different case', () => {
      const params = { term: 'EXECUTIVES' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match partial occupation code', () => {
      const params = { term: '11-10' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match partial occupation name', () => {
      const params = { term: 'exec' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should not match when search term is not found', () => {
      const params = { term: 'developer' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      expect(result).toBeNull();
    });

    it('should handle whitespace in search term', () => {
      const params = { term: '  chief  ' };
      const data = { text: '11-1011 - Chief Executives' };

      const result = matcherFunction(params, data);

      // The matcher checks if the text contains the search term (after lowercase)
      // Since '  chief  ' is not trimmed before the indexOf check, it won't match
      expect(result).toBeNull();

      // But empty whitespace should return all data
      const emptyResult = matcherFunction({ term: '   ' }, data);
      expect(emptyResult).toBe(data);
    });

    it('should match multiple words in occupation name', () => {
      const params = { term: 'marketing managers' };
      const data = { text: '11-2021 - Marketing Managers' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match hyphenated occupation codes', () => {
      const params = { term: '11-20' };
      const data = { text: '11-2021 - Marketing Managers' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });

    it('should match when search term appears in the middle of text', () => {
      const params = { term: 'and' };
      const data = { text: '11-1021 - General and Operations Managers' };

      const result = matcherFunction(params, data);

      expect(result).toBe(data);
    });
  });

  describe('Search edge cases', () => {
    it('should handle empty occupation list', () => {
      const occupations: Array<{ code: string; name: string }> = [];

      expect(() => controller['populateOccupationDropdown'](occupations)).not.toThrow();

      expect(uiService.showNotification).toHaveBeenCalledWith({
        type: 'success',
        message: 'Loaded 0 occupations',
        duration: 3000,
      });
    });

    it('should handle occupations with special characters in names', () => {
      const occupations = [
        {
          code: '11-9031',
          name: 'Education Administrators, Preschool and Childcare Center/Program',
        },
        { code: '11-9032', name: 'Education Administrators, Elementary and Secondary School' },
      ];

      controller['populateOccupationDropdown'](occupations);

      expect(document.createElement).toHaveBeenCalledWith('option');
      const appendCalls = mockSelect2Instance.append.mock.calls;
      const firstOption = appendCalls[0][0];
      expect(firstOption.value).toBe('11-9031');
      expect(firstOption.text).toBe(
        '11-9031 - Education Administrators, Preschool and Childcare Center/Program'
      );
    });

    it('should handle very long occupation names', () => {
      const longName = 'A'.repeat(100);
      const occupations = [{ code: '11-1011', name: longName }];

      controller['populateOccupationDropdown'](occupations);

      expect(document.createElement).toHaveBeenCalledWith('option');
      const appendCalls = mockSelect2Instance.append.mock.calls;
      const firstOption = appendCalls[0][0];
      expect(firstOption.value).toBe('11-1011');
      expect(firstOption.text).toBe(`11-1011 - ${longName}`);
    });

    it('should match special characters in search', () => {
      const occupations = [
        {
          code: '11-9031',
          name: 'Education Administrators, Preschool and Childcare Center/Program',
        },
      ];

      controller['populateOccupationDropdown'](occupations);

      const select2Call = mockSelect2Instance.select2.mock.calls[0][0];
      const matcherFunction = select2Call.matcher;

      // Test matching with comma
      expect(
        matcherFunction(
          { term: 'administrators,' },
          { text: '11-9031 - Education Administrators, Preschool and Childcare Center/Program' }
        )
      ).toBeTruthy();

      // Test matching with slash
      expect(
        matcherFunction(
          { term: 'center/program' },
          { text: '11-9031 - Education Administrators, Preschool and Childcare Center/Program' }
        )
      ).toBeTruthy();
    });

    it('should handle numeric-only search terms', () => {
      const occupations = mockOccupationIdsResponse.occupations;
      controller['populateOccupationDropdown'](occupations);

      const select2Call = mockSelect2Instance.select2.mock.calls[0][0];
      const matcherFunction = select2Call.matcher;

      // Test matching just numbers
      expect(
        matcherFunction({ term: '1011' }, { text: '11-1011 - Chief Executives' })
      ).toBeTruthy();

      expect(
        matcherFunction({ term: '2021' }, { text: '11-2021 - Marketing Managers' })
      ).toBeTruthy();
    });
  });

  describe('Integration with API data format', () => {
    it('should handle new API response structure correctly', async () => {
      mockCacheService.get.mockReturnValue(null);
      mockApiService.getOccupationIds.mockResolvedValue(mockOccupationIdsResponse);

      await controller['loadOccupationIds']();

      // Verify the occupations array was extracted correctly
      expect(mockCacheService.set).toHaveBeenCalledWith(
        'occupation_ids',
        mockOccupationIdsResponse.occupations,
        24 * 60 * 60
      );

      // Verify option elements were created with correct format
      expect(document.createElement).toHaveBeenCalledWith('option');
      const appendCalls = mockSelect2Instance.append.mock.calls;
      const firstOption = appendCalls[0][0];
      expect(firstOption.value).toBe('11-1011');
      expect(firstOption.text).toBe('11-1011 - Chief Executives');
    });

    it('should cache the new occupation format correctly', async () => {
      const cachedOccupations = mockOccupationIdsResponse.occupations;
      mockCacheService.get.mockReturnValue(cachedOccupations);

      await controller['loadOccupationIds']();

      // Should use cached data
      expect(mockApiService.getOccupationIds).not.toHaveBeenCalled();

      // Should still populate dropdown correctly
      expect(document.createElement).toHaveBeenCalledWith('option');
      const appendCalls = mockSelect2Instance.append.mock.calls;
      const firstOption = appendCalls[0][0];
      expect(firstOption.value).toBe('11-1011');
      expect(firstOption.text).toBe('11-1011 - Chief Executives');
    });
  });

  describe('Dropdown change handler with new format', () => {
    it('should load occupation data when occupation is selected by code', async () => {
      const occupations = mockOccupationIdsResponse.occupations;
      controller['populateOccupationDropdown'](occupations);

      // Simulate selecting an occupation
      const occupationCode = '11-1011';
      const loadOccupationDataSpy = vi.spyOn(controller as any, 'loadOccupationData');

      // Find the change handler that was set up
      const setupDropdownHandlerSpy = vi.spyOn(controller as any, 'setupDropdownChangeHandler');
      controller['populateOccupationDropdown'](occupations);

      // Get the callback function from the spy
      const changeHandlerCall = setupDropdownHandlerSpy.mock.calls[0];
      if (!changeHandlerCall) {
        throw new Error('setupDropdownChangeHandler was not called');
      }
      const changeCallback = changeHandlerCall[1] as (_value: string | null) => void;

      // Call the change handler with an occupation code
      await changeCallback(occupationCode);

      expect(loadOccupationDataSpy).toHaveBeenCalledWith(occupationCode);
    });

    it('should clear map when no occupation is selected', () => {
      const occupations = mockOccupationIdsResponse.occupations;
      const clearMapSpy = vi.spyOn(controller as any, 'clearMap');

      // Setup dropdown
      controller['populateOccupationDropdown'](occupations);

      // Get the change handler
      const setupDropdownHandlerSpy = vi.spyOn(controller as any, 'setupDropdownChangeHandler');
      controller['populateOccupationDropdown'](occupations);
      const changeHandlerCall = setupDropdownHandlerSpy.mock.calls[0];
      if (!changeHandlerCall) {
        throw new Error('setupDropdownChangeHandler was not called');
      }
      const changeCallback = changeHandlerCall[1] as (_value: string | null) => void;

      // Call with null/empty value
      changeCallback(null);

      expect(clearMapSpy).toHaveBeenCalled();
    });
  });
});
