import { defineStore } from 'pinia';
import { ref } from 'vue';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
}

interface Modal {
  title: string;
  content: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'warning' | 'danger';
}

export const useUIStore = defineStore('ui', () => {
  const loadingStates = ref<Set<string>>(new Set());

  function isLoading(id: string): boolean {
    return loadingStates.value.has(id);
  }

  function showLoading(id: string, _message?: string): void {
    // _message parameter is reserved for future use when we add loading messages
    loadingStates.value.add(id);
  }

  function hideLoading(id: string): void {
    loadingStates.value.delete(id);
  }

  const notifications = ref<Notification[]>([]);
  const activeModal = ref<Modal | null>(null);

  function showSuccess(message: string): string {
    const id = `notification-${Date.now()}`;
    notifications.value.push({
      id,
      type: 'success',
      message,
    });
    return id;
  }

  function showError(message: string): string {
    const id = `notification-${Date.now()}`;
    notifications.value.push({
      id,
      type: 'error',
      message,
    });
    return id;
  }

  let modalResolve: ((value: boolean) => void) | null = null;

  function showModal(options: Modal): Promise<boolean> {
    return new Promise((resolve) => {
      activeModal.value = options;
      modalResolve = resolve;
    });
  }

  function confirmModal(): void {
    if (modalResolve) {
      modalResolve(true);
      modalResolve = null;
    }
    activeModal.value = null;
  }

  function cancelModal(): void {
    if (modalResolve) {
      modalResolve(false);
      modalResolve = null;
    }
    activeModal.value = null;
  }

  return {
    isLoading,
    showLoading,
    hideLoading,
    notifications,
    activeModal,
    showSuccess,
    showError,
    showModal,
    confirmModal,
    cancelModal,
  };
});
