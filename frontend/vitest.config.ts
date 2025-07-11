import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  // Reuse vite config
  root: '.',
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  test: {
    // Test environment
    environment: 'happy-dom',
    
    // Global test APIs
    globals: true,
    
    // Setup files
    setupFiles: ['./src/__tests__/setup.ts'],
    
    // Coverage configuration
    coverage: {
      enabled: true, // Enable coverage by default for CI
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './coverage',
      include: [
        'src/**/*.{js,ts}',
        '!src/**/*.d.ts',
        '!src/**/*-main.ts',
        '!src/main.ts',
        '!src/types/**',
      ],
      exclude: [
        'node_modules/',
        'dist/',
        'src/__tests__/**',
      ],
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
    
    // Reporter
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