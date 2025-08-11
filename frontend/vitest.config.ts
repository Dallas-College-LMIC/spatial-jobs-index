import { defineConfig } from 'vitest/config';
import { resolve } from 'path';
import { VitestReporter } from 'tdd-guard-vitest';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
    reporters: ['default', new VitestReporter(resolve(__dirname, '..'))],
  },
});
