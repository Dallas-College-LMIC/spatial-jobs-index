<template>
  <div class="filter-controls">
    <div class="filter-header">
      <h3>Filters</h3>
      <span v-if="activeFilterCount > 0" class="filter-count">
        {{ activeFilterCount }} active {{ activeFilterCount === 1 ? 'filter' : 'filters' }}
      </span>
    </div>

    <div class="filter-group">
      <div class="wage-filter">
        <label for="wage-level">Wage Level</label>
        <select
          id="wage-level"
          v-model="filters.wageLevel"
          @change="handleFilterChange"
        >
          <option value="all">All Wages</option>
          <option value="low">Low ($0-$30k)</option>
          <option value="medium">Medium ($30k-$60k)</option>
          <option value="high">High ($60k-$100k)</option>
          <option value="very-high">Very High ($100k+)</option>
        </select>
      </div>

      <div class="education-filter">
        <label for="education-level">Education Level</label>
        <select
          id="education-level"
          v-model="filters.educationLevel"
          @change="handleFilterChange"
        >
          <option value="all">All Education Levels</option>
          <option value="no-degree">No Degree</option>
          <option value="high-school">High School</option>
          <option value="associates">Associate's Degree</option>
          <option value="bachelors">Bachelor's Degree</option>
          <option value="masters">Master's Degree</option>
          <option value="doctorate">Doctorate</option>
        </select>
      </div>
    </div>

    <button
      class="reset-button"
      :disabled="activeFilterCount === 0"
      @click="resetFilters"
    >
      Reset Filters
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useOccupationStore } from '../stores/occupation';

interface FilterState {
  wageLevel: string;
  educationLevel: string;
}

const emit = defineEmits<{
  'filter-change': [filters: FilterState];
  'filter-reset': [];
}>();

const occupationStore = useOccupationStore();

const filters = ref<FilterState>({
  wageLevel: 'all',
  educationLevel: 'all'
});

const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.value.wageLevel !== 'all') count++;
  if (filters.value.educationLevel !== 'all') count++;
  return count;
});

const handleFilterChange = () => {
  // Update store
  occupationStore.setFilterOptions(filters.value);

  // Emit event
  emit('filter-change', { ...filters.value });
};

const resetFilters = () => {
  filters.value = {
    wageLevel: 'all',
    educationLevel: 'all'
  };

  // Update store
  occupationStore.setFilterOptions(filters.value);

  // Emit events
  emit('filter-reset');
  emit('filter-change', { ...filters.value });
};
</script>

<style scoped>
.filter-controls {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.filter-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.filter-count {
  font-size: 0.875rem;
  color: #666;
  background-color: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.wage-filter,
.education-filter {
  display: flex;
  flex-direction: column;
}

.wage-filter label,
.education-filter label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #495057;
}

.wage-filter select,
.education-filter select {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: white;
  font-size: 0.875rem;
}

.reset-button {
  width: 100%;
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.reset-button:hover:not(:disabled) {
  background-color: #5a6268;
}

.reset-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (min-width: 768px) {
  .filter-group {
    flex-direction: row;
    gap: 1rem;
  }

  .wage-filter,
  .education-filter {
    flex: 1;
  }
}
</style>
