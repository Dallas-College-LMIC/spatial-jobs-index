<template>
  <nav class="navbar navbar-expand-lg navbar-dark g-0 p-0 m-0" id="banner">
    <a class="navbar-brand p-0" :href="BRANDING.homeUrl">
      <img :src="BRANDING.logoUrl" id="dc_logo" alt="Dallas College Logo" />
    </a>
    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#bannertoggle"
      aria-controls="bannertoggle"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse p-0 justify-content-start" id="bannertoggle">
      <ul class="navbar-nav p-0">
        <li><RouterLink class="nav-link" to="/">Project Home</RouterLink></li>
        <li><RouterLink class="nav-link" to="/wage-level">Job Access by Wage Level</RouterLink></li>
        <li><RouterLink class="nav-link" to="/occupation">Job Access by Occupation</RouterLink></li>
        <li><RouterLink class="nav-link" to="/school-of-study">Job Access by School of Study</RouterLink></li>
        <li><RouterLink class="nav-link" to="/travel-time">Travel Time Analysis</RouterLink></li>
      </ul>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { BRANDING } from '../../js/constants';
</script>

<style scoped>
/* Banner and Navigation Styles */
#banner {
  background-color: rgba(0, 51, 133, 1);
  z-index: 1000;
}

#dc_logo {
  height: 4rem;
}

.navbar-brand {
  margin-left: 1rem;
  margin-right: 1rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.navbar-toggler {
  border-width: 0.2rem;
  padding: 0.1rem;
  margin-right: 1rem;
}

.nav-link {
  font-size: 1rem;
  font-weight: bold;
  padding: 0.5rem 0.5rem 0.5rem 0.5rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  color: white;
  text-decoration: none;
}

.nav-link:hover {
  color: rgba(255, 255, 255, 0.8);
}

.nav-link.router-link-active {
  color: rgba(255, 255, 191, 1);
}
</style>
