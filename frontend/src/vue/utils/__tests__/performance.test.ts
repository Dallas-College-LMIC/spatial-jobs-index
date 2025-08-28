import { describe, it, expect } from 'vitest';

describe('Performance Monitoring', () => {
  it('should export a measurePerformance function', async () => {
    const module = await import('../performance');
    expect(typeof module.measurePerformance).toBe('function');
  });
});
