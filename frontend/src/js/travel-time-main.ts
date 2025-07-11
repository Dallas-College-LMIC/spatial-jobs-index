import '../styles/shared.css';
import { ErrorHandler } from './utils/errorHandler';
import { TravelTimeMapController } from './controllers/TravelTimeMapController';

// Set up global error handlers
window.addEventListener('error', (event) => {
  ErrorHandler.logError(event.error || new Error(event.message), 'Window Error', {
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
  });
});

window.addEventListener('unhandledrejection', (event) => {
  ErrorHandler.logError(
    event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
    'Unhandled Promise Rejection'
  );
});

// Initialize the map when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new TravelTimeMapController('mainmap');
  });
} else {
  new TravelTimeMapController('mainmap');
}
