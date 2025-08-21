<template>
  <div class="travel-time-page">
    <h1>Travel Time Analysis</h1>

    <div class="travel-time-container">
      <label for="travel-time">Travel Time (minutes):</label>
      <input
        id="travel-time"
        v-model.number="travelTime"
        type="number"
        min="0"
        max="120"
        data-testid="travel-time-input"
        class="travel-time-input"
        placeholder="Enter travel time in minutes"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const travelTime = ref(30);
</script>

<script lang="ts">
export default {
  name: 'TravelTimePage',
};
</script>

<style scoped>
.travel-time-page {
  padding: 2rem;
}

.travel-time-container label {
  display: block;
  margin-bottom: 0.5rem;
}

.travel-time-input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
