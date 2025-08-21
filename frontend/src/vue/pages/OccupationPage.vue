<template>
  <div>
    <h1>Occupation Access</h1>
    <OccupationSelect />
  </div>
</template>

<script setup lang="ts">
import OccupationSelect from '../components/OccupationSelect.vue';

defineOptions({
  name: 'OccupationPage',
});
</script>
