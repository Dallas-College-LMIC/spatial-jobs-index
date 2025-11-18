import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import OccupationPage from '../OccupationPage.vue';

// Mock MapManager to avoid Mapbox initialization
vi.mock('../../../js/mapUtils', () => ({
  MapManager: vi.fn().mockImplementation(() => ({
    addSource: vi.fn(),
    addLayer: vi.fn(),
    addPopupEvents: vi.fn(),
    onStyleLoad: vi.fn((callback) => callback()),
  })),
}));

describe('OccupationPage', () => {
  it('should render occupation select component', () => {
    const wrapper = mount(OccupationPage, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          OccupationMap: true,
        },
      },
    });

    expect(wrapper.findComponent({ name: 'OccupationSelect' }).exists()).toBe(true);
  });

  it('should render occupation map component', () => {
    const wrapper = mount(OccupationPage, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          OccupationSelect: true,
          OccupationMap: true,
        },
      },
    });

    expect(wrapper.findComponent({ name: 'OccupationMap' }).exists()).toBe(true);
  });

  it('should render legend panel', () => {
    const wrapper = mount(OccupationPage, {
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          OccupationSelect: true,
          OccupationMap: true,
        },
      },
    });

    expect(wrapper.find('.legend-panel').exists()).toBe(true);
    expect(wrapper.text()).toContain('Transit Travelshed Index - By Occupation');
  });
});
