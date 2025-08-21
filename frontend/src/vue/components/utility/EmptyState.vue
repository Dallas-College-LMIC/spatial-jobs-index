<template>
  <div class="empty-state">{{ message }}</div>
</template>

<script setup lang="ts">
defineProps<{
  message: string;
}>();
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 4px;
  margin: 1rem 0;
}
</style>
