import { createRouter as createVueRouter, createWebHistory } from 'vue-router';
import HomePage from '../pages/HomePage.vue';
import OccupationPage from '../pages/OccupationPage.vue';
import SchoolOfStudyPage from '../pages/SchoolOfStudyPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/occupation',
    name: 'Occupation',
    component: OccupationPage,
  },
  {
    path: '/school-of-study',
    name: 'SchoolOfStudy',
    component: SchoolOfStudyPage,
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
];

export function createRouter() {
  return createVueRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
  });
}
