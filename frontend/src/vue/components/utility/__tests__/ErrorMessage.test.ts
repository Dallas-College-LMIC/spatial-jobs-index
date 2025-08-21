import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ErrorMessage from '../ErrorMessage.vue';

describe('ErrorMessage', () => {
  it('displays error message', () => {
    const wrapper = mount(ErrorMessage, {
      props: {
        message: 'Something went wrong',
      },
    });

    expect(wrapper.text()).toContain('Something went wrong');
  });

  it('has error styling class', () => {
    const wrapper = mount(ErrorMessage, {
      props: {
        message: 'Error',
      },
    });

    expect(wrapper.classes()).toContain('error-message');
  });
});
