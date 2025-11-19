import { MAP_CONFIG, COLOR_SCHEMES } from './constants';
import mapboxgl from 'mapbox-gl';
import type { GeoJSONResponse } from '../types/api';
import type {
  MapboxMap,
  MapboxPopup,
  MapboxMapLayerMouseEvent,
  MapboxExpression,
} from '../types/mapbox';
import { isGeoJSONSource } from '../types/mapbox';

export class MapManager {
  public map!: MapboxMap;
  private containerId: string;
  private popup!: MapboxPopup;

  constructor(containerId: string) {
    this.containerId = containerId;
    this.initializeMap();
  }

  private initializeMap(): void {
    mapboxgl.accessToken = MAP_CONFIG.accessToken;

    this.map = new mapboxgl.Map({
      container: this.containerId,
      ...MAP_CONFIG,
    }) as MapboxMap;

    this.popup = new mapboxgl.Popup({
      closeButton: true,
      closeOnClick: false,
      anchor: 'bottom',
      offset: 0,
      maxWidth: 'none',
    }) as MapboxPopup;

    this.addControls();
  }

  private addControls(): void {
    const fullscreenControl = new mapboxgl.FullscreenControl({
      container: document.querySelector('body') as HTMLElement,
    });

    this.map.addControl(fullscreenControl, 'bottom-left');

    const navigationControl = new mapboxgl.NavigationControl({
      showCompass: true,
      showZoom: true,
      visualizePitch: true,
    });

    this.map.addControl(navigationControl, 'bottom-left');
  }

  addSource(
    sourceId: string,
    data: GeoJSONResponse | { type: string; features: GeoJSON.Feature[] }
  ): void {
    const source = this.map.getSource(sourceId);

    if (source && isGeoJSONSource(source)) {
      source.setData(
        data as
          | GeoJSON.FeatureCollection<GeoJSON.Geometry>
          | GeoJSON.Feature<GeoJSON.Geometry>
          | string
      );
    } else {
      this.map.addSource(sourceId, {
        type: 'geojson',
        data: data as
          | GeoJSON.FeatureCollection<GeoJSON.Geometry>
          | GeoJSON.Feature<GeoJSON.Geometry>
          | string,
      });
    }
  }

  private createLayerColor(propertyName: string): MapboxExpression {
    const layerColor: MapboxExpression = ['match', ['get', propertyName]];

    COLOR_SCHEMES.zscoreCategories.forEach((category, index) => {
      layerColor.push(category, COLOR_SCHEMES.zscoreColors[index]);
    });

    layerColor.push('#000000'); // fallback color
    return layerColor;
  }

  addLayer(
    layerId: string,
    sourceId: string,
    propertyName: string,
    visibility: 'visible' | 'none' = 'visible'
  ): void {
    if (this.map.getLayer(layerId)) {
      this.map.removeLayer(layerId);
    }

    this.map.addLayer({
      id: layerId,
      type: 'fill',
      source: sourceId,
      layout: {
        visibility: visibility,
      },
      paint: {
        'fill-color': this.createLayerColor(propertyName),
        'fill-outline-color': COLOR_SCHEMES.outlineColor,
      },
    });
  }

  setLayerVisibility(layerId: string, visibility: 'visible' | 'none'): void {
    if (this.map.getLayer(layerId)) {
      this.map.setLayoutProperty(layerId, 'visibility', visibility);
    }
  }

  addPopupEvents(layerId: string, title: string, scoreProperty: string): void {
    this.map.on('click', layerId, (e: MapboxMapLayerMouseEvent) => {
      const coordinates = e.lngLat;
      const features = e.features;

      if (!features || features.length === 0) {
        return;
      }

      const firstFeature = features[0];
      const properties = firstFeature?.properties;
      if (!properties) {
        return;
      }

      const score = properties[scoreProperty] as number | undefined;
      const jobCount = properties.jobs_2024_rawcount as number | undefined;
      const openingsCount = properties.openings_2024_rawcount as number | undefined;
      const earnings = properties.percentile_50th_earnings_2023_rawcount as number | undefined;

      // Calculate percentile from z-score using standard normal distribution
      // Percentile = Φ(z) * 100, where Φ is the cumulative distribution function
      const zScoreToPercentile = (z: number): number => {
        // Using error function approximation for CDF of standard normal
        const t = 1 / (1 + 0.2316419 * Math.abs(z));
        const d = 0.3989423 * Math.exp((-z * z) / 2);
        const prob =
          d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
        return Math.round((z > 0 ? 1 - prob : prob) * 100);
      };

      const percentile = score !== undefined && score !== null ? zScoreToPercentile(score) : null;

      const description = `
                <b>Tract: </b><span>${properties.geoid || properties.GEOID}</span><br>
                <b>${title}: </b><span>${score ? score.toFixed(2) : 'N/A'}</span><br>
                <b>Percentile of all DFW tracts: </b><span>${percentile !== null ? percentile + 'th' : 'N/A'}</span>
                <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
                <div style="margin-top: 10px;">
                    <b style="display: block; margin-bottom: 5px; font-size: 14px;">Job Summary</b>
                    <b>Number of Jobs (2024): </b><span>${jobCount ? jobCount.toFixed(0) : 'N/A'}</span><br>
                    <b>Job Openings (2024): </b><span>${openingsCount ? openingsCount.toFixed(0) : 'N/A'}</span><br>
                    <b>Median Earnings (2023): </b><span>${earnings ? '$' + earnings.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',') : 'N/A'}</span><br>
                    <b>Share of Jobs within Dallas County: </b><span style="color: #666;">Data pending</span>
                </div>
            `;

      this.popup.setLngLat(coordinates).setHTML(description).addTo(this.map);
    });

    this.map.on('mouseenter', layerId, () => {
      this.map.getCanvas().style.cursor = 'pointer';
    });

    this.map.on('mouseleave', layerId, () => {
      this.map.getCanvas().style.cursor = '';
    });
  }

  onStyleLoad(callback: () => void): void {
    this.map.on('style.load', callback);
  }
}
