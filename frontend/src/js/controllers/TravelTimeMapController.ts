import { BaseMapController } from './baseMapController';
import { ErrorHandler } from '../utils/errorHandler';
import type { MapClickEvent } from '../../types/mapbox';

interface IsochroneResponse {
  type: 'FeatureCollection';
  features: Array<{
    type: 'Feature';
    geometry: {
      type: 'Polygon' | 'MultiPolygon';
      coordinates: number[][][] | number[][][][];
    };
    properties: {
      time_category: string;
      color: string;
      geoid: string;
    };
  }>;
}

export class TravelTimeMapController extends BaseMapController {
  private isochroneSourceId = 'isochrones';
  private isochroneLayers: string[] = [];

  // Time band colors mapping - must match the time_category values from API
  private timeBandColors: Record<string, string> = {
    '< 5': '#1a9850',
    '5 ~ 10': '#66bd63',
    '10 ~ 15': '#a6d96a',
    '15 ~ 20': '#fdae61',
    '20 ~ 25': '#fee08b',
    '25 ~ 30': '#f46d43',
    '30 ~ 45': '#d73027',
    '> 45': '#a50026',
  };

  constructor(containerId: string) {
    super(containerId, 'census-tracts');
    this.initialize().catch((error) => {
      const err = error instanceof Error ? error : new Error(String(error));
      ErrorHandler.logError(err, 'Controller Initialization', {
        controller: 'TravelTimeMapController',
      });
    });
  }

  async initialize(): Promise<void> {
    await this.initializeMapWithEmptySource();

    // Add isochrone source
    this.mapManager.addSource(this.isochroneSourceId, {
      type: 'FeatureCollection',
      features: [],
    });

    // Load census tract data and set up everything in sequence
    await this.loadData({
      onAfterLoad: (data) => {
        // Data is already loaded into the 'census-tracts' source by loadData
        
        // Add census tract layers
        this.addCensusTractLayer();

        // Wait a moment for layers to be fully added before setting up events
        setTimeout(() => {
          // Setup click handler after layers are definitely added
          this.setupClickHandler();

          // Setup clear button
          this.setupClearButton();
        }, 100);
      },
    });
  }

  private addCensusTractLayer(): void {
    // Add fill layer for census tracts (transparent like NYC map)
    this.mapManager.map.addLayer({
      id: 'census-tracts-fill',
      type: 'fill',
      source: this.sourceId,
      paint: {
        'fill-color': 'transparent',
        'fill-opacity': 0,
      },
    });

    // Add outline layer for census tracts (light gray like NYC map)
    this.mapManager.map.addLayer({
      id: 'census-tracts-outline',
      type: 'line',
      source: this.sourceId,
      paint: {
        'line-color': '#cccccc',
        'line-width': 0.5,
        'line-opacity': 0.8,
      },
    });

    // Add hover highlight layer
    this.mapManager.map.addLayer({
      id: 'census-tracts-hover',
      type: 'line',
      source: this.sourceId,
      paint: {
        'line-color': '#000000',
        'line-width': 2,
        'line-opacity': 1,
      },
      filter: ['==', 'geoid', ''],
    });

    // Add selected tract highlight layer (thicker black outline)
    this.mapManager.map.addLayer({
      id: 'selected-tract',
      type: 'line',
      source: this.sourceId,
      paint: {
        'line-color': '#000000',
        'line-width': 3,
        'line-opacity': 1,
      },
      filter: ['==', 'geoid', ''],
    });
  }

  private setupClickHandler(): void {
    // Use general click handler and check for census tract features
    this.mapManager.map.on('click', async (e: any) => {
      // Query features at click point
      const features = this.mapManager.map.queryRenderedFeatures(e.point, {
        layers: ['census-tracts-fill']
      });
      
      if (!features || features.length === 0) {
        return;
      }

      const feature = features[0];
      
      // Handle both GEOID and geoid property names, and remove .0 suffix if present
      let geoid = feature?.properties?.GEOID || feature?.properties?.geoid;
      
      if (geoid && typeof geoid === 'string' && geoid.endsWith('.0')) {
        geoid = geoid.slice(0, -2);
      }

      if (!geoid) {
        console.error('No GEOID found in clicked feature', feature?.properties);
        return;
      }

      // Prevent multiple simultaneous requests
      if (this.isLoading) {
        return;
      }

      // Clear previous selection
      this.clearSelection();

      // Update selected tract display
      this.updateSelectedTractDisplay(geoid);

      // Highlight selected tract (use geoid with lowercase since that's what's in the data)
      this.mapManager.map.setFilter('selected-tract', ['==', 'geoid', geoid + '.0']);

      // Load isochrone data
      await this.loadIsochroneData(geoid);
    });

    // Change cursor and highlight on hover
    let hoveredTractId: string | null = null;
    
    this.mapManager.map.on('mousemove', 'census-tracts-fill', (e: any) => {
      if (e.features && e.features.length > 0) {
        const feature = e.features[0];
        const geoid = feature?.properties?.geoid;
        
        if (geoid && hoveredTractId !== geoid) {
          // Remove previous hover
          if (hoveredTractId) {
            this.mapManager.map.setFilter('census-tracts-hover', ['==', 'geoid', '']);
          }
          
          // Add new hover
          hoveredTractId = geoid;
          this.mapManager.map.setFilter('census-tracts-hover', ['==', 'geoid', geoid]);
          this.mapManager.map.getCanvas().style.cursor = 'pointer';
        }
      }
    });

    this.mapManager.map.on('mouseleave', 'census-tracts-fill', () => {
      if (hoveredTractId) {
        this.mapManager.map.setFilter('census-tracts-hover', ['==', 'geoid', '']);
        hoveredTractId = null;
      }
      this.mapManager.map.getCanvas().style.cursor = '';
    });
  }

  private setupClearButton(): void {
    const clearButton = document.getElementById('clear-selection');
    if (clearButton) {
      clearButton.addEventListener('click', () => {
        this.clearSelection();
      });
    }
  }

  private async loadIsochroneData(geoid: string): Promise<void> {
    // Cancel any existing load
    this.cancelCurrentLoad();

    // Create abort controller
    this.currentLoadController = this.apiService.createAbortController('isochrone-load');
    const signal = this.currentLoadController.signal;

    // Show loading state
    this.showLoading('loading', 'Loading travel times...');

    try {
      // Fetch isochrone data
      const response = (await this.apiService.getIsochroneData(geoid, signal)) as IsochroneResponse;

      // Check if request was aborted
      if (signal.aborted) {
        return;
      }


      // Update isochrone source
      this.mapManager.addSource(this.isochroneSourceId, response as any);

      // Clear existing isochrone layers
      this.clearIsochroneLayers();

      // Add isochrone layers by time band (in reverse order for proper stacking)
      const timeBands = Object.keys(this.timeBandColors).reverse();

      for (const timeBand of timeBands) {
        const layerId = `isochrone-${timeBand.replace(/[<> ~]/g, '-')}`;
        this.isochroneLayers.push(layerId);

        this.mapManager.map.addLayer(
          {
            id: layerId,
            type: 'fill',
            source: this.isochroneSourceId,
            paint: {
              'fill-color': this.timeBandColors[timeBand],
              'fill-opacity': 0.6,
            },
            filter: ['==', 'time_category', timeBand],
          },
          'census-tracts-outline'
        ); // Add below census tract outline layer but above fill
      }

      // Add isochrone outlines
      const outlineLayerId = 'isochrone-outline';
      this.isochroneLayers.push(outlineLayerId);

      this.mapManager.map.addLayer(
        {
          id: outlineLayerId,
          type: 'line',
          source: this.isochroneSourceId,
          paint: {
            'line-color': '#333333',
            'line-width': 1,
            'line-opacity': 0.8,
          },
        },
        'census-tracts-hover'
      );
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));

      // Handle abort errors gracefully
      if (err.name === 'AbortError') {
        console.log('Isochrone request aborted');
        return;
      }

      ErrorHandler.logError(err, 'Isochrone Data Loading', {
        geoid,
      });

      // Show error message
      ErrorHandler.showInlineError(
        this.containerId,
        `Failed to load travel time data for tract ${geoid}. Click to retry.`,
        () => this.loadIsochroneData(geoid)
      );
    } finally {
      this.isLoading = false;
      this.hideLoading('loading');

      if (this.currentLoadController && !this.currentLoadController.signal.aborted) {
        this.currentLoadController = null;
      }
    }
  }

  private clearIsochroneLayers(): void {
    // Remove all existing isochrone layers
    this.isochroneLayers.forEach((layerId) => {
      if (this.mapManager.map.getLayer(layerId)) {
        this.mapManager.map.removeLayer(layerId);
      }
    });
    this.isochroneLayers = [];
  }

  private clearSelection(): void {
    // Clear selected tract filter
    this.mapManager.map.setFilter('selected-tract', ['==', 'geoid', '']);

    // Clear isochrone layers
    this.clearIsochroneLayers();

    // Reset isochrone source
    this.mapManager.addSource(this.isochroneSourceId, {
      type: 'FeatureCollection',
      features: [],
    });

    // Hide selected tract display
    this.updateSelectedTractDisplay(null);

    // Cancel any ongoing requests
    this.cancelCurrentLoad();
  }

  private updateSelectedTractDisplay(geoid: string | null): void {
    const selectedTractDiv = document.getElementById('selected-tract');
    const tractIdSpan = document.getElementById('tract-id');
    const clearButton = document.getElementById('clear-selection');

    if (selectedTractDiv && tractIdSpan && clearButton) {
      if (geoid) {
        tractIdSpan.textContent = geoid;
        selectedTractDiv.style.display = 'block';
        clearButton.style.display = 'block';
      } else {
        selectedTractDiv.style.display = 'none';
        clearButton.style.display = 'none';
      }
    }
  }

  protected getLayerIds(): string[] {
    return [
      'census-tracts-fill',
      'census-tracts-outline',
      'census-tracts-hover',
      'selected-tract',
      ...this.isochroneLayers,
    ];
  }
}

