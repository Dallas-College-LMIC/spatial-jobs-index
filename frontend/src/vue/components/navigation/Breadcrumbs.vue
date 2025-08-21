<template>
  <nav>
    <ol>
      <template v-for="(crumb, index) in breadcrumbs" :key="index">
        <li :class="['breadcrumb-item', { active: index === breadcrumbs.length - 1 }]">
          <RouterLink v-if="index < breadcrumbs.length - 1" :to="crumb.path">
            {{ crumb.label }}
          </RouterLink>
          <span v-else>{{ crumb.label }}</span>
        </li>
        <li v-if="index < breadcrumbs.length - 1" class="breadcrumb-divider">/</li>
      </template>
    </ol>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, RouterLink } from 'vue-router';

const route = useRoute();

const breadcrumbs = computed(() => {
  const crumbs = [];

  // Always add Home
  crumbs.push({ label: 'Home', path: '/' });

  // Add current route if not home
  if (route.path !== '/') {
    const meta = route.meta.breadcrumb;
    if (meta) {
      crumbs.push({ label: meta as string, path: route.path });
    }
  }

  return crumbs;
});
</script>

<style scoped>
nav {
  padding: 0.5rem 0;
}

ol {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
}

.breadcrumb-item {
  font-size: 0.875rem;
}

.breadcrumb-item a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}

.breadcrumb-item.active {
  color: #6c757d;
}

.breadcrumb-divider {
  margin: 0 0.5rem;
  color: #6c757d;
}
</style>
