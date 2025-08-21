import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock the App component
vi.mock('../components/App.vue', () => ({
  default: {
    template: '<router-view></router-view>',
  },
}));

// Create a mock router instance
const mockRouterInstance = {
  install: vi.fn(),
  push: vi.fn(),
  currentRoute: { value: { path: '/' } },
};

// Mock the router
vi.mock('../router', () => ({
  createRouter: vi.fn(() => mockRouterInstance),
}));

describe('Vue Application Router Integration', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    // Create a container for the Vue app
    container = document.createElement('div');
    container.id = 'app';
    document.body.appendChild(container);
  });

  afterEach(() => {
    // Clean up
    if (container.parentNode) {
      document.body.removeChild(container);
    }
  });

  it('should set up Vue Router when initializing the app', async () => {
    const { createRouter } = await import('../router');
    const { initVueApp } = await import('../main');

    initVueApp('#app');

    // Check that createRouter was called
    expect(createRouter).toHaveBeenCalled();

    // Check that router install was called with the app
    expect(mockRouterInstance.install).toHaveBeenCalled();
  });
});
