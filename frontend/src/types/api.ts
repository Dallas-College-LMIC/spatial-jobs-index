// API Response Types

export interface OccupationIdsResponse {
  occupations: Array<{
    code: string;
    name: string;
  }>;
}

export interface SchoolOfStudyIdsResponse {
  school_ids: string[];
}

export interface GeoJSONProperties {
  GEOID: string;
  [key: string]: string | number | null; // Dynamic properties for z-scores
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][] | number[][][][]; // GeoJSON coordinate arrays
  };
  properties: GeoJSONProperties;
}

export interface GeoJSONResponse {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

// Z-score categories
export type ZScoreCategory =
  | '<-2.5SD'
  | '-2.5SD ~ -1.5SD'
  | '-1.5SD ~ -0.5SD'
  | '-0.5SD ~ +0.5SD'
  | '+0.5SD ~ +1.5SD'
  | '+1.5SD ~ +2.5SD'
  | '>=+2.5SD';

export interface LayerConfig {
  id: string;
  visibility: 'visible' | 'none';
  property: string;
  title: string;
  scoreProperty: string;
}

// Coordinate types for GeoJSON geometry
export type Position = [longitude: number, latitude: number];
export type PolygonCoordinates = Position[][];
export type MultiPolygonCoordinates = PolygonCoordinates[];

// Isochrone-specific types
export interface IsochroneProperties {
  geoid: string;
  travel_time_minutes: number;
  [key: string]: string | number;
}

export interface IsochroneFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: PolygonCoordinates | MultiPolygonCoordinates;
  };
  properties: IsochroneProperties;
}

export interface IsochroneResponse {
  type: 'FeatureCollection';
  features: IsochroneFeature[];
}

// Enhanced error type for API errors
export interface ApiError extends Error {
  status?: number;
  statusText?: string;
  body?: string;
  endpoint?: string;
  url?: string;
}
