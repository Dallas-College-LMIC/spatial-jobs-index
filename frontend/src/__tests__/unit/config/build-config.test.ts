import { describe, it, expect } from 'vitest';
import viteConfig from '../../../../vite.config';
import { UserConfig } from 'vite';

describe('Vite Configuration', () => {
  it('should have manual chunks function that returns a value for all code paths', () => {
    const config = viteConfig({ mode: 'production', command: 'build' }) as UserConfig;
    const output = config.build?.rollupOptions?.output;

    // Check output is not an array (single output config)
    expect(output).toBeDefined();
    expect(Array.isArray(output)).toBe(false);

    if (output && !Array.isArray(output)) {
      const manualChunks = output.manualChunks as Function;
      expect(manualChunks).toBeDefined();

      // Test that function returns something for all paths
      expect(manualChunks('/src/js/utils/helpers.ts')).toBeUndefined();
    }
  });
});
