export function useMapInteractions(map: any) {
  const addClickHandler = (layerId: string, handler: Function) => {
    map.on('click', layerId, handler);
  };

  const addHoverEffect = (layerId: string) => {
    map.on('mouseenter', layerId, () => {
      map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', layerId, () => {
      map.getCanvas().style.cursor = '';
    });
  };

  const removeClickHandler = (layerId: string, handler: Function) => {
    map.off('click', layerId, handler);
  };

  return {
    addClickHandler,
    removeClickHandler,
    addHoverEffect,
  };
}
