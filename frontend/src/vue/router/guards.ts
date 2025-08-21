import type { Router } from 'vue-router';

export function setupNavigationGuards(router: Router): Router {
  // Navigation logging guard
  router.beforeEach((to, from, next) => {
    const fromName = String(from.name) || 'Home';
    const toName = String(to.name) || to.path;
    console.log(`[Navigation] ${fromName} → ${toName}`);
    next();
  });

  // Scroll to top after each navigation
  router.afterEach(() => {
    window.scrollTo(0, 0);
  });

  return router;
}
