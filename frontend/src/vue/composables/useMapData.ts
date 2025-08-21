export function useMapData(map: any) {
  const addDataSource = (sourceId: string, sourceData: any) => {
    map.addSource(sourceId, sourceData);
  };

  const updateSourceData = (sourceId: string, data: any) => {
    const source = map.getSource(sourceId);
    if (source) {
      source.setData(data);
    }
  };

  return {
    addDataSource,
    updateSourceData,
  };
}
