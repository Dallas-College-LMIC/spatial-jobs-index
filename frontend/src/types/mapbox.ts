import {
  Map,
  Popup,
  LngLat,
  LngLatLike,
  MapMouseEvent,
  MapLayerMouseEvent,
  GeoJSONSource,
  NavigationControl,
  FullscreenControl,
  Layer,
  FillLayer,
  LineLayer,
  SymbolLayer,
  CircleLayer,
  HeatmapLayer,
  FillExtrusionLayer,
  RasterLayer,
  HillshadeLayer,
  BackgroundLayer,
  Expression,
  Source,
  AnySourceData,
  ImageSource,
  VideoSource,
  CanvasSource,
  Style,
  PointLike,
  Anchor,
  GeoJSONSourceSpecification,
  VectorSourceSpecification,
  RasterSourceSpecification,
  RasterDEMSourceSpecification,
  FillPaint,
  FillLayout,
  LinePaint,
  LineLayout,
  SymbolPaint,
  SymbolLayout,
  CirclePaint,
  CircleLayout,
  LngLatBoundsLike,
  FitBoundsOptions,
  GeoJSONFeature as MapboxGeoJSONFeature,
} from 'mapbox-gl';

// Re-export commonly used Mapbox types with cleaner aliases
export type MapboxMap = Map;
export type MapboxPopup = Popup;
export type MapboxLngLat = LngLat;
export type MapboxLngLatLike = LngLatLike;
export type MapboxMapMouseEvent = MapMouseEvent;
export type MapboxMapLayerMouseEvent = MapLayerMouseEvent;
export type MapboxGeoJSONSource = GeoJSONSource;
// Use GeoJSONSourceSpecification from v3
export type MapboxGeoJSONSourceOptions = Partial<GeoJSONSourceSpecification>;
export type MapboxNavigationControl = NavigationControl;
export type MapboxFullscreenControl = FullscreenControl;
// EventData is a simple object type in v3
export type MapboxEventData = Record<string, any>;
// ErrorEvent is handled differently in v3
export interface MapboxErrorEvent {
  error: Error;
  target: Map;
  type: 'error';
}

// Layer types
export type MapboxLayer = Layer;
export type MapboxFillLayer = FillLayer;
export type MapboxLineLayer = LineLayer;
export type MapboxSymbolLayer = SymbolLayer;
export type MapboxCircleLayer = CircleLayer;
export type MapboxHeatmapLayer = HeatmapLayer;
export type MapboxFillExtrusionLayer = FillExtrusionLayer;
export type MapboxRasterLayer = RasterLayer;
export type MapboxHillshadeLayer = HillshadeLayer;
export type MapboxBackgroundLayer = BackgroundLayer;

// Paint and layout property types are available in v3
export type MapboxFillPaint = FillPaint;
export type MapboxFillLayout = FillLayout;
export type MapboxLinePaint = LinePaint;
export type MapboxLineLayout = LineLayout;
export type MapboxSymbolPaint = SymbolPaint;
export type MapboxSymbolLayout = SymbolLayout;
export type MapboxCirclePaint = CirclePaint;
export type MapboxCircleLayout = CircleLayout;

// Expression types
export type MapboxExpression = Expression;
// StyleFunction replaced by expressions in v3
export type MapboxStyleFunction = Expression;

// Source types
export type MapboxAnySource = Source;
export type MapboxAnySourceData = AnySourceData;
// Use source specification types from v3
export type MapboxGeoJSONSourceRaw = GeoJSONSourceSpecification;
export type MapboxVectorSource = VectorSourceSpecification;
export type MapboxRasterSource = RasterSourceSpecification;
export type MapboxRasterDemSource = RasterDEMSourceSpecification;
export type MapboxImageSource = ImageSource;
export type MapboxVideoSource = VideoSource;
export type MapboxCanvasSource = CanvasSource;

// Style types
export type MapboxStyle = Style;
// StyleOptions not exported in v3, define a compatible interface
export interface MapboxStyleOptions {
  validate?: boolean;
  localFontFamily?: string;
  localIdeographFontFamily?: string;
}

// Control position types
export type MapboxControlPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';

// Custom interfaces for the SJI webapp
export interface ChoroplethLayerConfig {
  id: string;
  sourceId: string;
  sourceLayer?: string;
  paint: MapboxFillPaint;
  layout?: MapboxFillLayout;
  beforeId?: string;
}

export interface ChoroplethOutlineLayerConfig {
  id: string;
  sourceId: string;
  sourceLayer?: string;
  paint: MapboxLinePaint;
  layout?: MapboxLineLayout;
  beforeId?: string;
}

export interface MapClickEvent extends MapboxMapLayerMouseEvent {
  features?: MapboxGeoJSONFeature[]; // Use GeoJSONFeature type from v3
}

export interface MapLoadEvent {
  target: MapboxMap;
  type: 'load';
}

export interface MapErrorEvent {
  error: Error;
  target: MapboxMap;
  type: 'error';
}

export interface LayerVisibilityOptions {
  layerId: string;
  visibility: 'visible' | 'none';
}

export interface PopupOptions {
  coordinates: MapboxLngLatLike;
  html: string;
  className?: string;
  offset?: PointLike;
  closeButton?: boolean;
  closeOnClick?: boolean;
  closeOnMove?: boolean;
  focusAfterOpen?: boolean;
  anchor?: Anchor;
  maxWidth?: string;
}

export interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface MapViewState {
  center: MapboxLngLatLike;
  zoom: number;
  bearing?: number;
  pitch?: number;
}

// Type guards
export function isGeoJSONSource(
  source: MapboxAnySource | undefined
): source is MapboxGeoJSONSource {
  return source?.type === 'geojson';
}

export function isFillLayer(layer: MapboxLayer): layer is MapboxFillLayer {
  return layer.type === 'fill';
}

export function isLineLayer(layer: MapboxLayer): layer is MapboxLineLayer {
  return layer.type === 'line';
}

export function isSymbolLayer(layer: MapboxLayer): layer is MapboxSymbolLayer {
  return layer.type === 'symbol';
}

export function isCircleLayer(layer: MapboxLayer): layer is MapboxCircleLayer {
  return layer.type === 'circle';
}

// Utility types for expressions
export type ColorExpression = string | MapboxExpression;
export type NumberExpression = number | MapboxExpression;
export type BooleanExpression = boolean | MapboxExpression;
export type StringExpression = string | MapboxExpression;

// Z-score category types specific to SJI webapp
export type ZScoreCategory = '-2.5' | '-1.5' | '-0.5' | '0.5' | '1.5' | '2.5';

export interface ZScoreCategoryColors {
  '-2.5': string;
  '-1.5': string;
  '-0.5': string;
  '0.5': string;
  '1.5': string;
  '2.5': string;
}

// Feature properties interface for census tracts
export interface CensusTractProperties {
  GEOID: string;
  [key: string]: any; // Dynamic properties for different z-score fields
}

export interface CensusTractFeature
  extends GeoJSON.Feature<GeoJSON.Geometry, CensusTractProperties> {
  id?: string | number;
}

export interface CensusTractFeatureCollection
  extends GeoJSON.FeatureCollection<GeoJSON.Geometry, CensusTractProperties> {
  features: CensusTractFeature[];
}

// Map initialization options
export interface MapInitOptions {
  container: string | HTMLElement;
  style: string;
  center: MapboxLngLatLike;
  zoom: number;
  maxBounds?: LngLatBoundsLike;
  minZoom?: number;
  maxZoom?: number;
  bearing?: number;
  pitch?: number;
  interactive?: boolean;
  hash?: boolean;
  attributionControl?: boolean;
  customAttribution?: string | string[];
  logoPosition?: MapboxControlPosition;
  failIfMajorPerformanceCaveat?: boolean;
  preserveDrawingBuffer?: boolean;
  antialias?: boolean;
  refreshExpiredTiles?: boolean;
  bounds?: LngLatBoundsLike;
  fitBoundsOptions?: FitBoundsOptions;
  trackResize?: boolean;
  renderWorldCopies?: boolean;
  bearingSnap?: number;
  pitchWithRotate?: boolean;
  clickTolerance?: number;
  fadeDuration?: number;
  crossSourceCollisions?: boolean;
  accessToken?: string;
  locale?: any;
  testMode?: boolean;
}
// Test comment
