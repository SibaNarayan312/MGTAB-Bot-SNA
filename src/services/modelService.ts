import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { ModelPerformanceResponse } from '../types/model';

export const modelService = {
  async getModelPerformance(): Promise<ModelPerformanceResponse> {
    if (FORCE_MOCK) {
      return mockAdapter.getModelPerformance();
    }
    try {
      const response = await apiClient.get<ModelPerformanceResponse>('/model-performance');
      return response.data;
    } catch {
      console.warn('[modelService] FastAPI /model-performance unavailable, falling back to mock adapter.');
      return mockAdapter.getModelPerformance();
    }
  },
};
