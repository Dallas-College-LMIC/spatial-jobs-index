import { describe, it, expect } from 'vitest';
import { createApp } from 'vue';
import { setupStores } from '../../stores';

describe('Pinia Store Configuration', () => {
  it('should setup pinia with persistence plugin', () => {
    const app = createApp({});
    const store = setupStores(app);
    expect(store).toBeDefined();
  });
});
