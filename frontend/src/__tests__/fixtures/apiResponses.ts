import type { OccupationIdsResponse, GeoJSONResponse } from '../../types/api';

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
