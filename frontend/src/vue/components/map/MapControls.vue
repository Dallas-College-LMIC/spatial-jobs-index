<template>
  <div class="map-controls">
    <button data-testid="zoom-in" :disabled="disabled" @click="$emit('zoom-in')">+</button>
    <button data-testid="zoom-out" :disabled="disabled" @click="$emit('zoom-out')">-</button>
    <button data-testid="fit-bounds" :disabled="disabled" @click="$emit('fit-bounds')">Fit</button>

    <div v-for="layer in layers" :key="layer.id" class="layer-control">
      <input
        type="checkbox"
        :data-testid="`layer-toggle-${layer.id}`"
        :checked="layer.visible"
        @change="$emit('toggle-layer', layer.id)"
      />
      <label>{{ layer.name }}</label>
    </div>
  </div>
</template>

<script setup lang="ts">
interface MapLayer {
  id: string;
  name: string;
  visible: boolean;
}

defineProps<{
  layers?: MapLayer[],
  disabled?: boolean
}>();

defineEmits<{
  'zoom-in': [],
  'zoom-out': [],
  'fit-bounds': [],
  'toggle-layer': [id: string]
}>();
</script>

<style scoped>
.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1;
  background: white;
  border-radius: 4px;
  padding: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

button {
  display: block;
  width: 32px;
  height: 32px;
  margin-bottom: 4px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

button:hover:not(:disabled) {
  background: #f0f0f0;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.layer-control {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ddd;
}

.layer-control label {
  margin-left: 4px;
  font-size: 12px;
}
</style>
