import { ref } from 'vue';
import mapboxgl from 'mapbox-gl';

export function useMapbox() {
  const map = ref<any>(null);
  const isMapLoaded = ref(false);

  const initializeMap = async (container: HTMLElement, config: any = {}) => {
    map.value = new mapboxgl.Map({
      container,
      style: config.style || 'mapbox://styles/mapbox/streets-v11',
      center: config.center,
      zoom: config.zoom,
    });

    if (config.controls?.navigation) {
      const navControl = new mapboxgl.NavigationControl();
      map.value.addControl(navControl);
    }

    return new Promise((resolve) => {
      map.value.on('load', () => {
        isMapLoaded.value = true;
        resolve(map.value);
      });
    });
  };

  const destroyMap = () => {
    if (map.value) {
      map.value.remove();
      map.value = null;
      isMapLoaded.value = false;
    }
  };

  return {
    map,
    isMapLoaded,
    initializeMap,
    destroyMap,
    getMapboxToken: () => '',
  };
}
