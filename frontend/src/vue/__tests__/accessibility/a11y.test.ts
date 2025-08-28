import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import axe from 'axe-core';
import AppHeader from '../../components/AppHeader.vue';

describe('Accessibility Tests', () => {
  beforeEach(() => {
    // Clean up document body before each test
    document.body.innerHTML = '';
  });

  async function checkAccessibility(wrapper: any) {
    document.body.appendChild(wrapper.element);
    const results = await axe.run(wrapper.element);
    return results.violations;
  }

  it('AppHeader should have no accessibility violations', async () => {
    const wrapper = mount(AppHeader, {
      props: {
        title: 'Test Application',
      },
    });

    const violations = await checkAccessibility(wrapper);
    expect(violations).toHaveLength(0);
  });
});
