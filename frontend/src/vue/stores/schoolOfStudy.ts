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
      const apiService = new ApiService();
      const response = await apiService.getSchoolOfStudyIds();
      this.schoolIds = response.school_ids;
    },

    async fetchSchoolData(categoryCode: string) {
      this.selectedSchoolId = categoryCode;

      const apiService = new ApiService();
      const controller = apiService.createAbortController('school-data');
      const response = await apiService.getSchoolOfStudyData(categoryCode, controller.signal);

      this.schoolData = response;
    },
  },
});
