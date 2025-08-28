<template>
  <div>
    <select
      :value="modelValue"
      @change="handleChange"
      :disabled="store.isLoading"
      aria-label="Select an occupation"
    >
      <option value="">Select an occupation...</option>
      <option
        v-for="occupation in store.occupations"
        :key="occupation.code"
        :value="occupation.code"
      >
        {{ occupation.name }}
      </option>
    </select>
    <span v-if="store.isLoading" class="loading-indicator">Loading...</span>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useOccupationStore } from '../stores/occupation';

interface Props {
  modelValue?: string;
}

defineProps<Props>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const store = useOccupationStore();

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  emit('update:modelValue', target.value);
  store.selectedOccupationId = target.value;
};

onMounted(() => {
  store.fetchOccupationIds();
});

// Expose for testing
defineExpose({
  handleChange
});
</script>
