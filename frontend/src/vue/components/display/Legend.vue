<template>
  <div class="legend">
    <h3 data-testid="legend-title">{{ title }}</h3>
    <ul class="legend-items">
      <li v-for="item in items" :key="item.label" data-testid="legend-item">
        <span
          data-testid="legend-color"
          class="legend-color"
          :style="{ backgroundColor: item.color }"
        ></span>
        <span data-testid="legend-label">{{ item.label }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
interface LegendItem {
  label: string;
  color: string;
}

interface Props {
  title: string;
  items: LegendItem[];
}

defineProps<Props>();
</script>

<style scoped>
.legend-items {
  list-style: none;
  margin: 0;
  padding: 0;
}

.legend-color {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-right: 8px;
}
</style>
