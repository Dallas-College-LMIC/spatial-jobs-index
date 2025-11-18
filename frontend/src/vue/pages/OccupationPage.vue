<template>
  <div class="occupation-page">
    <div class="map-container-wrapper">
      <OccupationMap :occupationId="store.selectedOccupationId || undefined" />
    </div>
    <div class="legend-panel" id="legend">
      <div class="container g-0">
        <div class="row g-0 justify-content-start">
          <div class="col-auto header-text">
            Transit Travelshed Index - By Occupation
          </div>
        </div>
        <div class="row g-0 justify-content-center">
          <div class="col-12">
            <OccupationSelect v-model="selectedOccupation" />
          </div>
        </div>
        <div class="row g-0 justify-content-center">
          <hr />
          <div class="col-12">
            <img src="/images/colorbar.png" class="colorbar" alt="Color scale legend" />
          </div>
        </div>
        <div class="row g-0 justify-content-center">
          <hr />
          <div class="col-auto">
            <a
              class="btn btn-primary btn-sm export-btn"
              :href="exportUrl"
              target="_blank"
              :class="{ disabled: !store.selectedOccupationId }"
            >
              Export
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import OccupationSelect from '../components/OccupationSelect.vue';
import OccupationMap from '../components/map/OccupationMap.vue';
import { useOccupationStore } from '../stores/occupation';
import { ApiService } from '../../js/api';

defineOptions({
  name: 'OccupationPage',
});

const store = useOccupationStore();
const selectedOccupation = ref<string>('');
const apiService = new ApiService();

// Watch for selection changes and fetch data
watch(selectedOccupation, (newValue) => {
  if (newValue) {
    store.fetchOccupationData(newValue);
  }
});

// Compute export URL
const exportUrl = computed(() => {
  if (!store.selectedOccupationId) return '#';
  return apiService.getOccupationExportUrl(store.selectedOccupationId);
});
</script>

<style scoped>
.occupation-page {
  position: relative;
  width: 100%;
  height: calc(100vh - 6rem); /* Subtract header height */
}

.map-container-wrapper {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
}

.legend-panel {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: auto;
  max-height: 90%;
  padding: 1rem;
  color: rgba(0, 0, 0, 0.9);
  background-color: rgba(255, 255, 255, 0.95);
  font-size: 0.9rem;
  overflow: auto;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  z-index: 10;
}

.header-text {
  font-weight: bold;
  margin-bottom: 1rem;
}

.row {
  margin-top: 1rem;
}

.colorbar {
  width: 100%;
  max-width: 15rem;
}

.export-btn {
  background-color: rgba(229, 38, 38, 0.9);
  border-style: none;
  margin-bottom: 1rem;
  width: 8rem;
}

.export-btn:hover:not(.disabled) {
  background-color: rgba(229, 38, 38, 1);
}

.export-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

hr {
  margin: 1rem 0;
  border: none;
  border-top: 1px solid #ddd;
}
</style>
