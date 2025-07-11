// Wait for the map to be fully loaded
setTimeout(() => {
    // Find the map instance
    const mapContainer = document.getElementById('mainmap');
    if (\!mapContainer || \!mapContainer._mapboxMap) {
        console.log('Map not found');
        return;
    }
    
    const map = mapContainer._mapboxMap;
    
    // Get the center of the map
    const center = map.getCenter();
    
    // Simulate a click at the center
    const point = map.project(center);
    
    // Query features at that point
    const features = map.queryRenderedFeatures(point, {
        layers: ['census-tracts-fill']
    });
    
    if (features.length > 0) {
        console.log('Found census tract:', features[0].properties);
        
        // Trigger the click event
        const clickEvent = {
            lngLat: center,
            point: point,
            features: features,
            originalEvent: {
                preventDefault: () => {},
                stopPropagation: () => {}
            }
        };
        
        map.fire('click', clickEvent);
    } else {
        console.log('No census tract found at center');
    }
}, 3000);
EOF < /dev/null
