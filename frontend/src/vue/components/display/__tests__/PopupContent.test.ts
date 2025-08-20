import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import PopupContent from '../PopupContent.vue';

describe('PopupContent', () => {
  it('renders title and description', () => {
    const wrapper = mount(PopupContent, {
      props: {
        title: 'Census Tract 123',
        description: 'Dallas County',
        data: {},
      },
    });

    expect(wrapper.find('[data-testid="popup-title"]').text()).toBe('Census Tract 123');
    expect(wrapper.find('[data-testid="popup-description"]').text()).toBe('Dallas County');
  });

  it('renders data properties', () => {
    const data = {
      'Total Jobs': 1500,
      'Average Wage': '$65,000',
      'Education Level': "Bachelor's Degree",
    };

    const wrapper = mount(PopupContent, {
      props: {
        title: 'Tract Info',
        data,
      },
    });

    const dataItems = wrapper.findAll('[data-testid="data-item"]');
    expect(dataItems).toHaveLength(3);

    expect(dataItems[0]?.find('[data-testid="data-label"]').text()).toBe('Total Jobs');
    expect(dataItems[0]?.find('[data-testid="data-value"]').text()).toBe('1500');
  });

  it('renders without description when not provided', () => {
    const wrapper = mount(PopupContent, {
      props: {
        title: 'Title Only',
      },
    });

    expect(wrapper.find('[data-testid="popup-title"]').text()).toBe('Title Only');
    expect(wrapper.find('[data-testid="popup-description"]').text()).toBe('');
  });
});
