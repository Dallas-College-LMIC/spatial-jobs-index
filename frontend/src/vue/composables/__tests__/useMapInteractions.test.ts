import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useMapInteractions } from '../useMapInteractions';

describe('useMapInteractions', () => {
  let mockMap: any;

  beforeEach(() => {
    mockMap = {
      on: vi.fn(),
      off: vi.fn(),
      getCanvas: vi.fn(() => ({
        style: { cursor: '' },
      })),
      queryRenderedFeatures: vi.fn(),
    };
    vi.clearAllMocks();
  });

  it('should add click handler to map', () => {
    const { addClickHandler } = useMapInteractions(mockMap);
    const handler = vi.fn();

    addClickHandler('test-layer', handler);

    expect(mockMap.on).toHaveBeenCalledWith('click', 'test-layer', handler);
  });

  it('should add hover effect to layer', () => {
    const { addHoverEffect } = useMapInteractions(mockMap);

    addHoverEffect('test-layer');

    // Should add mouseenter handler
    expect(mockMap.on).toHaveBeenCalledWith('mouseenter', 'test-layer', expect.any(Function));
    // Should add mouseleave handler
    expect(mockMap.on).toHaveBeenCalledWith('mouseleave', 'test-layer', expect.any(Function));
  });

  it('should remove click handler from map', () => {
    const { removeClickHandler } = useMapInteractions(mockMap);
    const handler = vi.fn();

    removeClickHandler('test-layer', handler);

    expect(mockMap.off).toHaveBeenCalledWith('click', 'test-layer', handler);
  });
});
