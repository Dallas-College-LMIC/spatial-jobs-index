import type {
  OccupationIdsResponse,
  GeoJSONResponse,
  SchoolOfStudyIdsResponse,
} from '../../types/api';

export const mockOccupationIdsResponse: OccupationIdsResponse = {
  occupations: [
    { code: '11-1011', name: 'Chief Executives' },
    { code: '11-1021', name: 'General and Operations Managers' },
    { code: '11-2011', name: 'Advertising and Promotions Managers' },
    { code: '11-2021', name: 'Marketing Managers' },
    { code: '11-2022', name: 'Sales Managers' },
    { code: '11-3011', name: 'Administrative Services Managers' },
    { code: '11-3021', name: 'Computer and Information Systems Managers' },
    { code: '11-3031', name: 'Financial Managers' },
    { code: '11-3051', name: 'Industrial Production Managers' },
    { code: '11-3061', name: 'Purchasing Managers' },
    { code: '11-3071', name: 'Transportation, Storage, and Distribution Managers' },
    { code: '11-3121', name: 'Human Resources Managers' },
    { code: '11-3131', name: 'Training and Development Managers' },
    { code: '11-9021', name: 'Construction Managers' },
    { code: '11-9031', name: 'Education Administrators, Preschool and Childcare Center/Program' },
    { code: '11-9032', name: 'Education Administrators, Elementary and Secondary School' },
    { code: '11-9033', name: 'Education Administrators, Postsecondary' },
    { code: '11-9039', name: 'Education Administrators, All Other' },
    { code: '11-9041', name: 'Architectural and Engineering Managers' },
    { code: '11-9051', name: 'Food Service Managers' },
  ],
};

export const mockGeoJSONResponse: GeoJSONResponse = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        GEOID: '48001950100',
        occupation_id_zscore: 1.25,
        occupation_id_zscore_cat: '+1.0 - +1.5SD',
        all_jobs_zscore: 0.75,
        all_jobs_zscore_cat: '+0.5 - +1.0SD',
        living_wage_zscore: -0.5,
        living_wage_zscore_cat: '-1.0 - -0.5SD',
        not_living_wage_zscore: 2.1,
        Not_Living_Wage_zscore_cat: '+1.5 - +2.5SD',
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-97.0336, 32.8999],
            [-97.0336, 32.9099],
            [-97.0236, 32.9099],
            [-97.0236, 32.8999],
            [-97.0336, 32.8999],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        GEOID: '48001950200',
        occupation_id_zscore: -1.75,
        occupation_id_zscore_cat: '-2.5 - -1.5SD',
        all_jobs_zscore: -2.8,
        all_jobs_zscore_cat: '< -2.5SD',
        living_wage_zscore: 0.25,
        living_wage_zscore_cat: '-0.5 - +0.5SD',
        not_living_wage_zscore: -0.75,
        Not_Living_Wage_zscore_cat: '-1.0 - -0.5SD',
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-97.0236, 32.8999],
            [-97.0236, 32.9099],
            [-97.0136, 32.9099],
            [-97.0136, 32.8999],
            [-97.0236, 32.8999],
          ],
        ],
      },
    },
  ],
};

export const mockEmptyGeoJSONResponse: GeoJSONResponse = {
  type: 'FeatureCollection',
  features: [],
};

export const mockIsochroneResponse = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-97.0336, 32.8999],
            [-97.0336, 32.9099],
            [-97.0236, 32.9099],
            [-97.0236, 32.8999],
            [-97.0336, 32.8999],
          ],
        ],
      },
      properties: {
        time_band: '< 5 min',
        travel_time_minutes: 3,
      },
    },
    {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-97.0436, 32.8899],
            [-97.0436, 32.9199],
            [-97.0136, 32.9199],
            [-97.0136, 32.8899],
            [-97.0436, 32.8899],
          ],
        ],
      },
      properties: {
        time_band: '5-10 min',
        travel_time_minutes: 7,
      },
    },
    {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-97.0536, 32.8799],
            [-97.0536, 32.9299],
            [-97.0036, 32.9299],
            [-97.0036, 32.8799],
            [-97.0536, 32.8799],
          ],
        ],
      },
      properties: {
        time_band: '10-15 min',
        travel_time_minutes: 12,
      },
    },
    {
      type: 'Feature',
      geometry: {
        type: 'MultiPolygon',
        coordinates: [
          [
            [
              [-97.0636, 32.8699],
              [-97.0636, 32.9399],
              [-96.9936, 32.9399],
              [-96.9936, 32.8699],
              [-97.0636, 32.8699],
            ],
          ],
        ],
      },
      properties: {
        time_band: '15-20 min',
        travel_time_minutes: 18,
      },
    },
  ],
};

export const mockSchoolOfStudyIdsResponse: SchoolOfStudyIdsResponse = {
  school_ids: ['BHGT', 'CAED', 'CE', 'EDU', 'ETMS', 'HS', 'LPS', 'MIT'],
};

export const mockSchoolOfStudyGeoJSONResponse: GeoJSONResponse = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: {
        GEOID: '48113020100',
        category: 'ETMS',
        openings_2024_zscore: 1.5,
        jobs_2024_zscore: 0.8,
        openings_2024_zscore_color: '+1.0 - +1.5SD',
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-96.797, 32.7767],
            [-96.797, 32.7867],
            [-96.787, 32.7867],
            [-96.787, 32.7767],
            [-96.797, 32.7767],
          ],
        ],
      },
    },
    {
      type: 'Feature',
      properties: {
        GEOID: '48113020200',
        category: 'ETMS',
        openings_2024_zscore: -0.3,
        jobs_2024_zscore: 1.2,
        openings_2024_zscore_color: '-0.5 - +0.5SD',
      },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [-96.787, 32.7767],
            [-96.787, 32.7867],
            [-96.777, 32.7867],
            [-96.777, 32.7767],
            [-96.787, 32.7767],
          ],
        ],
      },
    },
  ],
};
