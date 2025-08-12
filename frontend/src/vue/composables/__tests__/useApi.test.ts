import { describe, it, expect, vi } from 'vitest';
import { useApi } from '../useApi';

describe('useApi', () => {
  it('should initialize with correct default state', () => {
    const { data, loading, error } = useApi();

    expect(data.value).toBeNull();
    expect(loading.value).toBe(false);
    expect(error.value).toBeNull();
  });

  it('should fetch data successfully', async () => {
    const mockData = { id: 1, name: 'Test' };
    const { data, loading, error, execute } = useApi();

    // Mock successful response
    const mockFetch = vi.fn().mockResolvedValue(mockData);

    // Execute the request
    const result = await execute('/test', mockFetch);

    expect(result).toEqual(mockData);
    expect(data.value).toEqual(mockData);
    expect(loading.value).toBe(false);
    expect(error.value).toBeNull();
  });

  it('should provide abort functionality', () => {
    const { abort, abortController } = useApi();

    // Create a mock controller
    const mockController = new AbortController();
    abortController.value = mockController;

    // Call abort
    abort();

    // Controller should be aborted
    expect(mockController.signal.aborted).toBe(true);
    expect(abortController.value).toBeNull();
  });

  it('should handle errors correctly', async () => {
    const mockError = new Error('Network error');
    const { data, loading, error, execute } = useApi();

    // Mock failed response
    const mockFetch = vi.fn().mockRejectedValue(mockError);

    // Execute the request
    const result = await execute('/test', mockFetch);

    expect(result).toBeNull();
    expect(data.value).toBeNull();
    expect(loading.value).toBe(false);
    expect(error.value).toEqual(mockError);
  });
});
