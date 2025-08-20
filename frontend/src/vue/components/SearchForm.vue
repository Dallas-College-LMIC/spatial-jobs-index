<template>
  <form @submit.prevent="handleSubmit" class="search-form">
    <div class="form-group">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search..."
        class="search-input"
        @input="updateSearchQuery"
      />
    </div>

    <div class="form-group">
      <OccupationSelect
        v-model="selectedOccupation"
        @update:modelValue="clearValidationError"
      />
    </div>

    <div class="form-group">
      <SchoolOfStudySelect
        v-model="selectedSchool"
        @update:modelValue="clearValidationError"
      />
    </div>

    <div v-if="validationError" class="validation-error">
      {{ validationError }}
    </div>

    <button
      type="submit"
      :disabled="isLoading"
      class="search-button"
    >
      {{ isLoading ? 'Searching...' : 'Search' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useOccupationStore } from '../stores/occupation';
import OccupationSelect from './OccupationSelect.vue';
import SchoolOfStudySelect from './SchoolOfStudySelect.vue';

interface Props {
  isLoading?: boolean;
}

interface SearchEvent {
  searchQuery: string;
  occupationId: string;
  schoolId: string;
}

defineProps<Props>();

const emit = defineEmits<{
  search: [data: SearchEvent];
}>();

const occupationStore = useOccupationStore();

const searchQuery = ref('');
const selectedOccupation = ref('');
const selectedSchool = ref('');
const validationError = ref('');

const updateSearchQuery = () => {
  occupationStore.setSearchQuery(searchQuery.value);
};

const clearValidationError = () => {
  validationError.value = '';
};

const handleSubmit = () => {
  // Validate form
  if (!selectedOccupation.value && !selectedSchool.value && !searchQuery.value) {
    validationError.value = 'Please select an occupation or school of study';
    return;
  }

  validationError.value = '';

  // Emit search event
  emit('search', {
    searchQuery: searchQuery.value,
    occupationId: selectedOccupation.value,
    schoolId: selectedSchool.value,
  });
};
</script>

<style scoped>
.search-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.search-input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.validation-error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.search-button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.search-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
