<template>
  <div
    :id="containerId"
    data-testid="map-container"
  />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import mapboxgl from 'mapbox-gl';
import { MAP_CONFIG } from '../../../js/constants';

interface Props {
  containerId?: string;
}

const props = withDefaults(defineProps<Props>(), {
  containerId: 'map',
});

const emit = defineEmits<{
  'map-loaded': [map: mapboxgl.Map];
}>();

const mapInstance = ref<mapboxgl.Map | null>(null);

onMounted(() => {
  // Set access token
  mapboxgl.accessToken = MAP_CONFIG.accessToken;

  // Initialize map
  const map = new mapboxgl.Map({
    container: props.containerId,
    style: MAP_CONFIG.style,
    center: MAP_CONFIG.center,
    zoom: MAP_CONFIG.zoom,
  });

  mapInstance.value = map;

  // Add navigation controls
  const navigationControl = new mapboxgl.NavigationControl();
  const fullscreenControl = new mapboxgl.FullscreenControl();

  map.addControl(navigationControl, 'bottom-left');
  map.addControl(fullscreenControl, 'bottom-left');

  // Emit event when map is loaded
  map.on('style.load', () => {
    emit('map-loaded', map);
  });
});

onUnmounted(() => {
  if (mapInstance.value) {
    mapInstance.value.remove();
    mapInstance.value = null;
  }
});
</script>
