import { describe, it, expect } from 'vitest';
import { add } from '../mathUtils';

describe('mathUtils', () => {
  describe('add', () => {
    it('should add two positive numbers', () => {
      expect(add(2, 3)).toBe(5);
    });
  });
});
