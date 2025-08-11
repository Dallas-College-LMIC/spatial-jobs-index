import { defineStore } from 'pinia';
import type { GeoJSONResponse } from '../../types/api';
import { ApiService } from '../../js/api';

interface Occupation {
  code: string;
  name: string;
}

interface OccupationState {
  occupations: Occupation[];
  selectedOccupationId: string | null;
  occupationData: GeoJSONResponse | null;
  isLoading: boolean;
  error: string | null;
  searchQuery: string;
  filterOptions: Record<string, unknown>;
}

export const useOccupationStore = defineStore('occupation', {
  state: (): OccupationState => ({
    occupations: [],
    selectedOccupationId: null,
    occupationData: null,
    isLoading: false,
    error: null,
    searchQuery: '',
    filterOptions: {},
  }),

  getters: {
    filteredOccupations(state) {
      if (!state.searchQuery) {
        return state.occupations;
      }

      const query = state.searchQuery.toLowerCase();
      return state.occupations.filter((occ) => occ.name.toLowerCase().includes(query));
    },
  },

  actions: {
    setSelectedOccupation(occupationId: string) {
      this.selectedOccupationId = occupationId;
    },

    setSearchQuery(query: string) {
      this.searchQuery = query;
    },

    setFilterOptions(filters: Record<string, unknown>) {
      this.filterOptions = filters;
    },

    async fetchOccupationIds() {
      this.isLoading = true;
      try {
        const apiService = new ApiService();
        const response = await apiService.getOccupationIds();
        this.occupations = response.occupations;
      } catch (error) {
        if (error instanceof Error) {
          this.error = `Failed to load occupations: ${error.message}`;
        }
      } finally {
        this.isLoading = false;
      }
    },

    async fetchOccupationData(occupationId: string) {
      this.selectedOccupationId = occupationId;

      const apiService = new ApiService();
      const controller = apiService.createAbortController('occupation-data');
      const response = await apiService.getOccupationData(occupationId, controller.signal);

      this.occupationData = response;
    },
  },
});
