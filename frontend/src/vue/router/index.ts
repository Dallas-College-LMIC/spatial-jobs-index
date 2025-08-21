import { createRouter as createVueRouter, createWebHistory } from 'vue-router';
import { setupNavigationGuards } from './guards';
import HomePage from '../pages/HomePage.vue';
import OccupationPage from '../pages/OccupationPage.vue';
import SchoolOfStudyPage from '../pages/SchoolOfStudyPage.vue';
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
    component: OccupationPage,
    meta: { breadcrumb: 'Occupations' },
  },
  {
    path: '/school-of-study',
    name: 'SchoolOfStudy',
    component: SchoolOfStudyPage,
    meta: { breadcrumb: 'Schools of Study' },
  },
  {
    path: '/wage-level',
    name: 'WageLevel',
    component: { template: '<div>Wage Level Page</div>' }, // Placeholder
  },
  {
    path: '/travel-time',
    name: 'TravelTime',
    component: { template: '<div>Travel Time Page</div>' }, // Placeholder
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
