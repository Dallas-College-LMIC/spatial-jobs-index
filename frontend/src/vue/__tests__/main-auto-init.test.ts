import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock the App component
vi.mock('../components/App.vue', () => ({
  default: {
    template: '<div>Test App</div>',
  },
}));

// Mock the router
vi.mock('../router', () => ({
  createRouter: vi.fn(() => ({
    install: vi.fn(),
  })),
}));

describe('Vue Application Auto-Initialization', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    // Reset modules to ensure clean state
    vi.resetModules();

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

  it('should automatically initialize when DOM is already loaded', async () => {
    // Set document ready state to complete
    Object.defineProperty(document, 'readyState', {
      value: 'complete',
      writable: true,
      configurable: true,
    });

    // Import main.ts which should auto-initialize
    await import('../main');

    // Wait for next tick to ensure initialization happens
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Check that the app is mounted to #app
    const appElement = document.querySelector('#app');
    expect(appElement?.innerHTML).toContain('Test App');
  });
});
