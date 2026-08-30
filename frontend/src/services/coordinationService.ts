import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { CoordinationSummaryResponse } from '../types/coordination';

export const coordinationService = {
  async getCoordinationAnalysis(): Promise<CoordinationSummaryResponse> {
    if (FORCE_MOCK) {
      return mockAdapter.getCoordination();
    }
    try {
      const response = await apiClient.get<CoordinationSummaryResponse>('/coordination');
      return response.data;
    } catch {
      console.warn('[coordinationService] FastAPI /coordination unavailable, falling back to mock adapter.');
      return mockAdapter.getCoordination();
    }
  },
};
