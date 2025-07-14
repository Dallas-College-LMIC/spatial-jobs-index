import { WageMapController } from './wage';
import { AppInitializer } from './utils/appInitializer';
import { renderNavigation } from '../components/navigation';
import '../styles/shared.css';

// Setup global error handlers
AppInitializer.setupGlobalErrorHandlers();

// Render navigation
document.addEventListener('DOMContentLoaded', () => {
  renderNavigation('navigation-container', 'wage');
});

// Initialize the wage map controller
AppInitializer.initialize('mainmap', WageMapController, 'Wage Map');
