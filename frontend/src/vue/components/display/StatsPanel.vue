<template>
  <div class="stats-panel">
    <h3 data-testid="stats-title">{{ title }}</h3>
    <div v-for="stat in stats" :key="stat.label" data-testid="stat-item">
      <span data-testid="stat-icon">{{ stat.icon }}</span>
      <span data-testid="stat-label">{{ stat.label }}</span>
      <span data-testid="stat-value">{{ stat.value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  stats: any[];
}

defineProps<Props>();
</script>
