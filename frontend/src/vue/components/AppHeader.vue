<template>
  <header class="app-header">
    <h1>{{ title }}</h1>
  </header>
</template>

<script setup lang="ts">
interface Props {
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: 'Spatial Jobs Index'
})
</script>
