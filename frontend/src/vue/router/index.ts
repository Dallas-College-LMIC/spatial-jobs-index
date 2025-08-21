import { createRouter as createVueRouter, createWebHistory } from 'vue-router';
import HomePage from '../pages/HomePage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/occupation',
    name: 'Occupation',
    component: { template: '<div>Occupation</div>' }, // Placeholder component
  },
];

export function createRouter() {
  return createVueRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
  });
}
