import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock the App component to avoid router dependency in test
vi.mock('../components/App.vue', () => ({
  default: {
    template: '<div>Test App</div>',
  },
}));

vi.mock('../router', () => ({
  createRouter: () => ({
    install: vi.fn(),
  }),
}));

describe('Vue Application Initialization', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    // Create a container for the Vue app
    container = document.createElement('div');
    container.id = 'app';
    document.body.appendChild(container);
  });

  afterEach(() => {
    // Clean up
    document.body.removeChild(container);
  });

  it('should initialize Vue app on given selector', async () => {
    const { initVueApp } = await import('../main');
    const app = initVueApp('#app');

    // Check that app is mounted
    expect(app).toBeDefined();
    expect(app._container).toBe(container);
  });

  it('should set up Pinia store', async () => {
    const { initVueApp } = await import('../main');
    const app = initVueApp('#app');

    // Check that Pinia is installed (stored as a Symbol)
    const provides = app._context.provides;
    const piniaSymbol = Object.getOwnPropertySymbols(provides).find(
      (sym) => sym.description === 'pinia'
    );
    expect(piniaSymbol).toBeDefined();
    expect(provides[piniaSymbol!]).toBeDefined();
  });
});
