<template>
  <div class="wage-page">
    <h1>Wage Level Analysis</h1>

    <div class="wage-selector-container">
      <label for="wage-level">Select Wage Level:</label>
      <select
        id="wage-level"
        v-model="selectedWageLevel"
        data-testid="wage-selector"
        class="wage-selector"
      >
        <option value="">-- Select Wage Level --</option>
        <option value="low">Low ($0 - $30,000)</option>
        <option value="medium">Medium ($30,000 - $60,000)</option>
        <option value="high">High ($60,000 - $100,000)</option>
        <option value="very-high">Very High ($100,000+)</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Component state
const selectedWageLevel = ref('');
</script>

<script lang="ts">
export default {
  name: 'WagePage',
};
</script>

<style scoped>
.wage-page {
  padding: 2rem;
}

h1 {
  margin-bottom: 1.5rem;
  color: #333;
}

.wage-selector-container {
  margin-bottom: 2rem;
}

.wage-selector-container label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.wage-selector {
  width: 100%;
  max-width: 300px;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}
</style>
