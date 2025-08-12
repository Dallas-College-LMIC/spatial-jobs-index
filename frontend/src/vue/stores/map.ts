import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Map } from 'mapbox-gl';

export const useMapStore = defineStore('map', () => {
  // State
  const mapInstance = ref<Map | null>(null);
  const isMapLoaded = ref(false);
  const activeLayers = ref<string[]>([]);
  const dataSources = ref<Record<string, any>>({});
  const isPopupOpen = ref(false);
  const popupContent = ref<string | null>(null);

  // Actions
  function setMapInstance(map: Map | null) {
    mapInstance.value = map;
  }

  function setMapLoaded(loaded: boolean) {
    isMapLoaded.value = loaded;
  }

  function addLayer(layerId: string) {
    if (!activeLayers.value.includes(layerId)) {
      activeLayers.value.push(layerId);
    }
  }

  function removeLayer(layerId: string) {
    const index = activeLayers.value.indexOf(layerId);
    if (index > -1) {
      activeLayers.value.splice(index, 1);
    }
  }

  function addSource(sourceId: string, sourceData: any) {
    dataSources.value[sourceId] = sourceData;
  }

  return {
    // State
    mapInstance,
    isMapLoaded,
    activeLayers,
    dataSources,
    isPopupOpen,
    popupContent,

    // Actions
    setMapInstance,
    setMapLoaded,
    addLayer,
    removeLayer,
    addSource,
  };
});
