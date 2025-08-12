import { ApiService } from '../../js/api';
import { useApi } from './useApi';
import type { OccupationIdsResponse, GeoJSONResponse } from '../../types/api';

export function useOccupationApi() {
  const api = new ApiService();
  const occupationIdsApi = useApi<OccupationIdsResponse>();
  const occupationDataApi = useApi<GeoJSONResponse>();

  const fetchOccupationIds = async () => {
    return occupationIdsApi.execute('/occupation_ids', (_endpoint, signal) =>
      api.getOccupationIds(signal)
    );
  };

  const fetchOccupationData = async (occupationId: string) => {
    return occupationDataApi.execute(`/occupation_data/${occupationId}`, (_endpoint, signal) =>
      api.getOccupationData(occupationId, signal)
    );
  };

  return {
    fetchOccupationIds,
    fetchOccupationData,
    occupationIds: occupationIdsApi.data,
    occupationIdsLoading: occupationIdsApi.loading,
    occupationIdsError: occupationIdsApi.error,
    occupationData: occupationDataApi.data,
    occupationDataLoading: occupationDataApi.loading,
    occupationDataError: occupationDataApi.error,
  };
}
