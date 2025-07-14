import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the CSS import
vi.mock('../../styles/shared.css', () => ({}));

// Mock the navigation component
const mockRenderNavigation = vi.fn();
vi.mock('../../components/navigation', () => ({
  renderNavigation: mockRenderNavigation,
}));

describe('main.ts', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules(); // Reset module cache to allow fresh imports
  });

  it('should import successfully', async () => {
    // This test ensures the main.ts file can be imported without errors
    await import('../../js/main');
    expect(true).toBe(true);
  });

  it('should render navigation on DOMContentLoaded', async () => {
    // Mock addEventListener to immediately call the callback
    const addEventListenerSpy = vi
      .spyOn(document, 'addEventListener')
      .mockImplementation((event: string, callback: any) => {
        if (event === 'DOMContentLoaded') {
          callback();
        }
      });

    // Import the module to trigger the DOMContentLoaded listener
    await import('../../js/main');

    // Verify that addEventListener was called with DOMContentLoaded
    expect(addEventListenerSpy).toHaveBeenCalledWith('DOMContentLoaded', expect.any(Function));

    // Verify that navigation was rendered with correct parameters
    expect(mockRenderNavigation).toHaveBeenCalledWith('navigation-container', '');
  });
});
