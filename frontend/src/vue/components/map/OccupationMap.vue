<template>
  <div data-testid="occupation-map">
    <div v-if="loading" data-testid="loading-indicator">Loading...</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  occupationId?: string,
  loading?: boolean
}>();
</script>
