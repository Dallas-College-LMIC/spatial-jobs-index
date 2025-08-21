import { createRouter as createVueRouter, createWebHistory } from 'vue-router';
import { setupNavigationGuards } from './guards';
// Only eagerly load critical routes
import HomePage from '../pages/HomePage.vue';
import NotFoundPage from '../pages/NotFoundPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { breadcrumb: 'Home' },
  },
  {
    path: '/occupation',
    name: 'Occupation',
    component: () => import('../pages/OccupationPage.vue'),
    meta: { breadcrumb: 'Occupations' },
  },
  {
    path: '/school-of-study',
    name: 'SchoolOfStudy',
    component: () => import('../pages/SchoolOfStudyPage.vue'),
    meta: { breadcrumb: 'Schools of Study' },
  },
  {
    path: '/wage-level',
    name: 'WageLevel',
    component: () => import('../pages/WagePage.vue'),
    meta: { breadcrumb: 'Wage Levels' },
  },
  {
    path: '/travel-time',
    name: 'TravelTime',
    component: () => import('../pages/TravelTimePage.vue'),
    meta: { breadcrumb: 'Travel Time' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage,
  },
];

export function createRouter() {
  const router = createVueRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
  });

  // Setup navigation guards
  setupNavigationGuards(router);

  return router;
}
