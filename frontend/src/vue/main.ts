import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter } from './router';
import App from './components/App.vue';

export function initVueApp(selector: string = '#app') {
  const app = createApp(App);

  // Setup Pinia store
  const pinia = createPinia();
  app.use(pinia);

  // Setup Router
  const router = createRouter();
  app.use(router);

  const element = document.querySelector(selector);
  if (element) {
    app.mount(element);
  }
  return app;
}

// Initialize the Vue app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initVueApp();
  });
} else {
  // DOM is already loaded
  initVueApp();
}
