import { SchoolOfStudyMapController } from './school-of-study';
import { AppInitializer } from './utils/appInitializer';
import '../styles/shared.css';

// Setup global error handlers
AppInitializer.setupGlobalErrorHandlers();

// Initialize the school of study map controller
AppInitializer.initialize('mainmap', SchoolOfStudyMapController, 'School of Study Map')
  .then((controller) => {
    // Expose cache debugging to global scope for development
    if (
      process.env.NODE_ENV === 'development' &&
      controller instanceof SchoolOfStudyMapController
    ) {
      (window as any).schoolOfStudyMapDebug = {
        getCacheStats: () => controller.getCacheStats(),
        clearAllCaches: () => controller.clearAllCaches(),
        controller: controller,
      };
      console.log('🔧 Debug tools available at window.schoolOfStudyMapDebug');
    }
  })
  .catch((error) => {
    console.error('Failed to initialize school of study map:', error);
  });
