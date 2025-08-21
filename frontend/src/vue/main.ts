import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './components/App.vue';

export function initVueApp(selector: string = '#app') {
  const app = createApp(App);

  // Setup Pinia store
  const pinia = createPinia();
  app.use(pinia);

  const element = document.querySelector(selector);
  if (element) {
    app.mount(element);
  }
  return app;
}
