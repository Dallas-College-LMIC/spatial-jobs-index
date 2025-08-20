<template>
  <div class="popup-content">
    <h4 data-testid="popup-title">{{ title }}</h4>
    <p data-testid="popup-description">{{ description }}</p>
    <dl v-if="data">
      <div v-for="(value, key) in data" :key="key" data-testid="data-item">
        <dt data-testid="data-label">{{ key }}</dt>
        <dd data-testid="data-value">{{ value }}</dd>
      </div>
    </dl>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  description?: string;
  data?: Record<string, any>;
}

defineProps<Props>();
</script>
