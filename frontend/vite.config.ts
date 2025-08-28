import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig(({ mode }) => ({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },

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
      },
      output: {
        // Manual chunk splitting for better caching
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('@vue')) {
              return 'vue-vendor';
            }
            if (id.includes('mapbox-gl') || id.includes('@studiometa/vue-mapbox-gl')) {
              return 'mapbox-vendor';
            }
            if (id.includes('pinia')) {
              return 'state-vendor';
            }
            return 'vendor';
          }
          // Application chunks
          if (id.includes('/src/vue/stores/')) {
            return 'stores';
          }
          if (id.includes('/src/vue/components/map/')) {
            return 'map-components';
          }
          if (id.includes('/src/vue/components/')) {
            return 'components';
          }
          // Default chunk - return undefined for Vite to handle
          return undefined;
        },
        // Use content hash for better caching
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'chunks/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js'
      }
    },
    // Ensure source maps for debugging
    sourcemap: mode === 'development',
    // Optimize chunk size warnings
    chunkSizeWarningLimit: 500,
    // Enable minification and tree shaking in production
    minify: mode === 'production' ? 'terser' : false,
    terserOptions: mode === 'production' ? {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    } : undefined,
    // CSS code splitting
    cssCodeSplit: true,
    // Asset inlining threshold (4kb)
    assetsInlineLimit: 4096
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
