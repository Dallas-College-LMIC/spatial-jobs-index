import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUIStore } from '../ui';

describe('UI Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  describe('Loading States', () => {
    it('should show and hide loading state', () => {
      const store = useUIStore();

      expect(store.isLoading('test-id')).toBe(false);

      store.showLoading('test-id', 'Loading data...');
      expect(store.isLoading('test-id')).toBe(true);

      store.hideLoading('test-id');
      expect(store.isLoading('test-id')).toBe(false);
    });

    it('should handle multiple loading states', () => {
      const store = useUIStore();

      store.showLoading('test-1', 'Loading 1...');
      store.showLoading('test-2', 'Loading 2...');

      expect(store.isLoading('test-1')).toBe(true);
      expect(store.isLoading('test-2')).toBe(true);

      store.hideLoading('test-1');
      expect(store.isLoading('test-1')).toBe(false);
      expect(store.isLoading('test-2')).toBe(true);
    });
  });

  describe('Notifications', () => {
    it('should show success notification', () => {
      const store = useUIStore();

      const id = store.showSuccess('Operation successful!');
      expect(id).toBeDefined();
      expect(store.notifications).toBeDefined();
      expect(store.notifications.length).toBe(1);
      expect(store.notifications[0].type).toBe('success');
      expect(store.notifications[0].message).toBe('Operation successful!');
    });

    it('should show error notification', () => {
      const store = useUIStore();

      const id = store.showError('Operation failed!');
      expect(id).toBeDefined();
      expect(store.notifications.length).toBe(1);
      expect(store.notifications[0].type).toBe('error');
      expect(store.notifications[0].message).toBe('Operation failed!');
    });
  });

  describe('Modals', () => {
    it('should show and close modal', async () => {
      const store = useUIStore();

      expect(store.activeModal).toBeNull();

      const modalPromise = store.showModal({
        title: 'Confirm Action',
        content: 'Are you sure?',
      });

      expect(store.activeModal).toBeDefined();
      expect(store.activeModal?.title).toBe('Confirm Action');
      expect(store.activeModal?.content).toBe('Are you sure?');

      store.confirmModal();
      const result = await modalPromise;
      expect(result).toBe(true);
      expect(store.activeModal).toBeNull();
    });

    it('should handle modal cancellation', async () => {
      const store = useUIStore();

      const modalPromise = store.showModal({
        title: 'Cancel Test',
        content: 'Testing cancel',
      });

      store.cancelModal();
      const result = await modalPromise;
      expect(result).toBe(false);
      expect(store.activeModal).toBeNull();
    });
  });
});
