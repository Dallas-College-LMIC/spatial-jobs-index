<template>
  <select>
    <option value="">Select a school of study...</option>
  </select>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useSchoolOfStudyStore } from '../stores/schoolOfStudy';

const store = useSchoolOfStudyStore();

onMounted(() => {
  store.fetchSchoolIds();
});
</script>
