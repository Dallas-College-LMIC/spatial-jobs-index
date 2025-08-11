import { defineConfig } from 'vitest/config';
import { resolve } from 'path';
// import { VitestReporter } from 'tdd-guard-vitest';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@vue': resolve(__dirname, './src/vue'),
    },
  },
  test: {
    // Test environment
    environment: 'happy-dom',

    // Global test APIs
    globals: true,

    // Setup files - comment out for now to test
    // setupFiles: ['./src/__tests__/setup.ts'],

    // Coverage configuration
    coverage: {
      enabled: false, // Disable by default, enable with --coverage flag
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      include: [
        'src/**/*.{js,ts}',
        '!src/**/*.d.ts',
        '!src/**/*-main.ts',
        '!src/main.ts',
        '!src/types/**',
      ],
      exclude: ['node_modules/', 'dist/', 'src/__tests__/**'],
      thresholds: {
        branches: 70,
        functions: 70,
        lines: 75,
        statements: 75,
      },
    },

    // Test file patterns
    include: ['src/**/*.{test,spec}.{js,ts}'],

    // Exclude patterns
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],

    // Reporter - temporarily disabled to debug @vue/test-utils issue
    // reporters: ['default', new VitestReporter(resolve(__dirname, '..'))],
    reporters: ['default'],

    // Test timeout
    testTimeout: 10000,

    // Hook timeout
    hookTimeout: 10000,

    // Mock configuration
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,
  },
});
