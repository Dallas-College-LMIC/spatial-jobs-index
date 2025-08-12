<template>
  <div>
    <select @change="handleChange" :disabled="store.isLoading">
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
</script>
