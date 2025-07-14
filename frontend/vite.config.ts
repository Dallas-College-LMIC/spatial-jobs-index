import { defineConfig } from 'vite';

export default defineConfig(({ mode }) => ({
  // Development server configuration
  server: {
    port: 3000,
    open: true
  },

  // Build configuration
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: 'index.html',
        occupation: 'access_occupation.html',
        wage: 'access_wagelvl.html',
        schoolOfStudy: 'access_school_of_study.html',
        travelTime: 'travel_time.html'
      }
    },
    // Ensure source maps for debugging
    sourcemap: true
  },

  // Environment variable prefix (only VITE_ prefixed vars are exposed to client)
  envPrefix: 'VITE_',

  // Define additional environment variables if needed
  define: {
    // Add any runtime constants here
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  },

  // Base path for assets (useful for deployment)
  // Use BASE_PATH env var if set, otherwise use appropriate default
  base: process.env.BASE_PATH || (mode === 'production' ? '/spatial-jobs-index/' : '/'),

  // Asset handling
  assetsInclude: ['**/*.png', '**/*.jpg', '**/*.jpeg', '**/*.gif', '**/*.svg']
}));
