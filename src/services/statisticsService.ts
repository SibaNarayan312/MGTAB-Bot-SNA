import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { OverviewStatistics } from '../types/statistics';

export const statisticsService = {
  async getOverviewStatistics(): Promise<OverviewStatistics> {
    if (FORCE_MOCK) {
      return mockAdapter.getStatistics();
    }
    try {
      const response = await apiClient.get<OverviewStatistics>('/statistics');
      return response.data;
    } catch {
      console.warn('[statisticsService] FastAPI unavailable, falling back to MGTAB mock data.');
      return mockAdapter.getStatistics();
    }
  },
};
