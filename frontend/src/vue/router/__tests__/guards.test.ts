import { describe, it, expect, vi } from 'vitest';
import { createRouter, createMemoryHistory } from 'vue-router';
import { setupNavigationGuards } from '../guards';

describe('Router Navigation Guards', () => {
  it('should call beforeEach guard on navigation', async () => {
    const beforeEachSpy = vi.fn((_to, _from, next) => next());

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/test', component: { template: '<div>Test</div>' } },
      ],
    });

    router.beforeEach(beforeEachSpy);

    await router.push('/test');

    expect(beforeEachSpy).toHaveBeenCalled();
  });

  it('should log navigation changes', async () => {
    const consoleSpy = vi.spyOn(console, 'log');

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
        { path: '/test', name: 'Test', component: { template: '<div>Test</div>' } },
      ],
    });

    router.beforeEach((to, from, next) => {
      console.log(`Navigating from ${String(from.name) || '/'} to ${String(to.name) || to.path}`);
      next();
    });

    await router.push('/test');

    expect(consoleSpy).toHaveBeenCalledWith('Navigating from undefined to Test');
    consoleSpy.mockRestore();
  });

  it('should setup navigation guards', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }],
    });

    const result = setupNavigationGuards(router);

    expect(result).toBe(router);
  });

  it('should log navigation with guards', async () => {
    const consoleSpy = vi.spyOn(console, 'log');

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
        { path: '/test', name: 'Test', component: { template: '<div>Test</div>' } },
      ],
    });

    setupNavigationGuards(router);
    await router.push('/test');

    expect(consoleSpy).toHaveBeenCalledWith('[Navigation] undefined → Test');
    consoleSpy.mockRestore();
  });

  it('should handle scroll behavior on navigation', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
        { path: '/test', name: 'Test', component: { template: '<div>Test</div>' } },
      ],
    });

    const windowSpy = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});

    setupNavigationGuards(router);

    await router.push('/test');

    expect(windowSpy).toHaveBeenCalledWith(0, 0);
    windowSpy.mockRestore();
  });
});
