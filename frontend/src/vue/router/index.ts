import { createRouter as createVueRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: { template: '<div>Home</div>' }, // Placeholder component
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
