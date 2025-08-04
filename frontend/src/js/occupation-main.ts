import { OccupationMapController } from './occupation';
import { AppInitializer } from './utils/appInitializer';
import { renderNavigation } from '../components/navigation';
import '../styles/shared.css';

// Setup global error handlers
AppInitializer.setupGlobalErrorHandlers();

// Render navigation
document.addEventListener('DOMContentLoaded', () => {
  renderNavigation('navigation-container', 'occupation');
});

// Initialize the occupation map controller
const initializeOccupationMap = async () => {
  try {
    const controller = await AppInitializer.initialize(
      'mainmap',
      OccupationMapController,
      'Occupation Map'
    );

    // Expose cache debugging to global scope for development
    if (process.env.NODE_ENV === 'development' && controller instanceof OccupationMapController) {
      (window as any).occupationMapDebug = {
        getCacheStats: () => controller.getCacheStats(),
        clearAllCaches: () => controller.clearAllCaches(),
        controller: controller,
      };
      console.log('🔧 Debug tools available at window.occupationMapDebug');
    }
  } catch (error) {
    console.error('Failed to initialize occupation map:', error);
  }
};

initializeOccupationMap();
