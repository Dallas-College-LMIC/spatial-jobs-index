<template>
  <div class="occupation-map-container">
    <div id="occupation-map-container" ref="mapContainer" class="map-container" data-testid="occupation-map"></div>
    <div v-if="loading" class="loading-overlay" data-testid="loading-indicator">
      <div class="spinner"></div>
      <span>Loading map data...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import { MapManager } from '../../../js/mapUtils';
import { useOccupationStore } from '../../stores/occupation';
import { storeToRefs } from 'pinia';

const props = defineProps<{
  occupationId?: string;
}>();

const mapContainer = ref<HTMLElement | null>(null);
let mapManager: MapManager | null = null;

const store = useOccupationStore();
const { occupationData, isLoading: loading } = storeToRefs(store);

const SOURCE_ID = 'occupation-source';
const LAYER_ID = 'occupation-layer';

onMounted(() => {
  if (mapContainer.value) {
    // Initialize the map
    mapManager = new MapManager('occupation-map-container');

    // Wait for the map style to load before adding data
    mapManager.onStyleLoad(() => {
      if (occupationData.value) {
        updateMapData();
      }
    });
  }
});

// Watch for changes in occupation data
watch(occupationData, (newData) => {
  if (newData && mapManager) {
    updateMapData();
  }
});

// Watch for changes in selected occupation ID
watch(() => props.occupationId, (newId) => {
  if (newId) {
    store.fetchOccupationData(newId);
  }
});

function updateMapData() {
  if (!mapManager || !occupationData.value) return;

  // Add or update the data source
  mapManager.addSource(SOURCE_ID, occupationData.value);

  // Add or update the layer
  mapManager.addLayer(LAYER_ID, SOURCE_ID, 'zscore', 'visible');

  // Add popup interactions
  mapManager.addPopupEvents(LAYER_ID, 'Z-Score', 'zscore');
}

onBeforeUnmount(() => {
  // Cleanup if needed
  if (mapManager) {
    mapManager = null;
  }
});
</script>

<style scoped>
.occupation-map-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
}

.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  z-index: 1000;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #003385;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
