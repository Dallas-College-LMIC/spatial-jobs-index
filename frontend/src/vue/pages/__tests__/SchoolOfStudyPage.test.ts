import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import SchoolOfStudyPage from '../SchoolOfStudyPage.vue';

describe('SchoolOfStudyPage', () => {
  it('should render page title', () => {
    const wrapper = mount(SchoolOfStudyPage, {
      global: {
        plugins: [createTestingPinia()],
      },
    });

    expect(wrapper.find('h1').text()).toBe('School of Study Access');
  });
});
