/// <reference types="vite/client" />
/// <reference types="mapbox-gl" />

// Global type declarations

// Declare mapboxgl as global since it's loaded from CDN
declare global {
  const mapboxgl: typeof import('mapbox-gl');
}

// Vite environment variables
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
}

// Augment the global ImportMeta interface from Vite
declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export {};
