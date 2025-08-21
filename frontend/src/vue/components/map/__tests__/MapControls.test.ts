import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import MapControls from '../MapControls.vue';

describe('MapControls', () => {
  let wrapper: any;

  beforeEach(() => {
    wrapper = null;
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders zoom controls', () => {
    wrapper = mount(MapControls);

    expect(wrapper.find('[data-testid="zoom-in"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="zoom-out"]').exists()).toBe(true);
  });

  it('emits zoom-in event when zoom in button is clicked', async () => {
    wrapper = mount(MapControls);

    await wrapper.find('[data-testid="zoom-in"]').trigger('click');

    expect(wrapper.emitted('zoom-in')).toBeTruthy();
    expect(wrapper.emitted('zoom-in')?.length).toBe(1);
  });

  it('emits zoom-out event when zoom out button is clicked', async () => {
    wrapper = mount(MapControls);

    await wrapper.find('[data-testid="zoom-out"]').trigger('click');

    expect(wrapper.emitted('zoom-out')).toBeTruthy();
    expect(wrapper.emitted('zoom-out')?.length).toBe(1);
  });

  it('renders fit bounds button', () => {
    wrapper = mount(MapControls);

    expect(wrapper.find('[data-testid="fit-bounds"]').exists()).toBe(true);
  });

  it('emits fit-bounds event when fit bounds button is clicked', async () => {
    wrapper = mount(MapControls);

    await wrapper.find('[data-testid="fit-bounds"]').trigger('click');

    expect(wrapper.emitted('fit-bounds')).toBeTruthy();
    expect(wrapper.emitted('fit-bounds')?.length).toBe(1);
  });

  it('renders layer toggles when layers prop is provided', () => {
    const layers = [
      { id: 'layer1', name: 'Layer 1', visible: true },
      { id: 'layer2', name: 'Layer 2', visible: false },
    ];

    wrapper = mount(MapControls, {
      props: { layers },
    });

    const toggles = wrapper.findAll('[data-testid^="layer-toggle-"]');
    expect(toggles).toHaveLength(2);
  });

  it('shows layer as checked when visible is true', () => {
    const layers = [{ id: 'layer1', name: 'Layer 1', visible: true }];

    wrapper = mount(MapControls, {
      props: { layers },
    });

    const toggle = wrapper.find('[data-testid="layer-toggle-layer1"]');
    expect(toggle.element.checked).toBe(true);
  });

  it('emits toggle-layer event with layer id when checkbox is clicked', async () => {
    const layers = [{ id: 'layer1', name: 'Layer 1', visible: true }];

    wrapper = mount(MapControls, {
      props: { layers },
    });

    await wrapper.find('[data-testid="layer-toggle-layer1"]').trigger('change');

    expect(wrapper.emitted('toggle-layer')).toBeTruthy();
    expect(wrapper.emitted('toggle-layer')?.[0]).toEqual(['layer1']);
  });

  it('disables zoom controls when disabled prop is true', () => {
    wrapper = mount(MapControls, {
      props: { disabled: true },
    });

    expect(wrapper.find('[data-testid="zoom-in"]').element.disabled).toBe(true);
    expect(wrapper.find('[data-testid="zoom-out"]').element.disabled).toBe(true);
    expect(wrapper.find('[data-testid="fit-bounds"]').element.disabled).toBe(true);
  });
});
