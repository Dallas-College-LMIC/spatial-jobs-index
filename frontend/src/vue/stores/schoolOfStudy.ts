import { defineStore } from 'pinia';
import type { GeoJSONResponse } from '../../types/api';
import { ApiService } from '../../js/api';

interface SchoolOfStudyState {
  schoolIds: string[];
  selectedSchoolId: string | null;
  schoolData: GeoJSONResponse | null;
  isLoading: boolean;
  error: string | null;
  searchQuery: string;
}

export const useSchoolOfStudyStore = defineStore('schoolOfStudy', {
  state: (): SchoolOfStudyState => ({
    schoolIds: [],
    selectedSchoolId: null,
    schoolData: null,
    isLoading: false,
    error: null,
    searchQuery: '',
  }),

  actions: {
    async fetchSchoolIds() {
      this.isLoading = true;
      this.error = null;

      try {
        const apiService = new ApiService();
        const response = await apiService.getSchoolOfStudyIds();
        this.schoolIds = response.school_ids;
      } catch (error) {
        this.schoolIds = [];
        if (error instanceof Error) {
          this.error = `Failed to load school IDs: ${error.message}`;
        } else {
          this.error = 'Failed to load school IDs: Unknown error';
        }
      } finally {
        this.isLoading = false;
      }
    },

    async fetchSchoolData(categoryCode: string) {
      this.isLoading = true;
      this.error = null;
      this.selectedSchoolId = categoryCode;

      try {
        const apiService = new ApiService();
        const controller = apiService.createAbortController('school-data');
        const response = await apiService.getSchoolOfStudyData(categoryCode, controller.signal);

        this.schoolData = response;
      } catch (error) {
        this.schoolData = null;
        if (error instanceof Error) {
          this.error = `Failed to load school data: ${error.message}`;
        } else {
          this.error = 'Failed to load school data: Unknown error';
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
});
