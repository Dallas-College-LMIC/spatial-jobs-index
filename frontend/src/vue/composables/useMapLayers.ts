export function useMapLayers(map: any) {
  const addLayer = (layer: any) => {
    map.addLayer(layer);
  };

  const removeLayer = (layerId: string) => {
    map.removeLayer(layerId);
  };

  const toggleLayerVisibility = (layerId: string, visible: boolean) => {
    map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
  };

  return {
    addLayer,
    removeLayer,
    toggleLayerVisibility,
  };
}
