import { ref, Ref, onUnmounted } from 'vue';

export function useApi<T = any>() {
  const data: Ref<T | null> = ref(null);
  const loading = ref(false);
  const error: Ref<Error | null> = ref(null);
  const abortController: Ref<AbortController | null> = ref(null);

  const abort = () => {
    if (abortController.value) {
      abortController.value.abort();
      abortController.value = null;
    }
  };

  const execute = async (
    endpoint: string,
    fetcher: (endpoint: string, signal?: AbortSignal) => Promise<T>
  ): Promise<T | null> => {
    // Abort any previous request
    abort();

    // Create new abort controller
    abortController.value = new AbortController();

    loading.value = true;
    error.value = null;

    try {
      const result = await fetcher(endpoint, abortController.value.signal);
      data.value = result;
      return result;
    } catch (err) {
      error.value = err as Error;
      return null;
    } finally {
      loading.value = false;
    }
  };

  // Clean up on component unmount
  onUnmounted(() => {
    abort();
  });

  return {
    data,
    loading,
    error,
    execute,
    abort,
    abortController,
  };
}
