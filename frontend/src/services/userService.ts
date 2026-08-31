import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { UserProfile, PredictRequest, PredictResponse } from '../types/user';
import { NetworkGraphData } from '../types/network';

export const userService = {
  async getUser(userId: string): Promise<UserProfile> {
    if (FORCE_MOCK) {
      return mockAdapter.getUser(userId);
    }
    try {
      const response = await apiClient.get<UserProfile>(`/user/${userId}`);
      return response.data;
    } catch {
      console.warn(`[userService] FastAPI /user/${userId} unavailable, falling back to mock adapter.`);
      return mockAdapter.getUser(userId);
    }
  },

  async getUserNetwork(userId: string): Promise<NetworkGraphData> {
    if (FORCE_MOCK) {
      return mockAdapter.getUserNetwork(userId);
    }
    try {
      const response = await apiClient.get<NetworkGraphData>(`/user/${userId}/network`);
      return response.data;
    } catch {
      console.warn(`[userService] FastAPI /user/${userId}/network unavailable, falling back to mock adapter.`);
      return mockAdapter.getUserNetwork(userId);
    }
  },

  async predictUser(req: PredictRequest): Promise<PredictResponse> {
    if (FORCE_MOCK) {
      return mockAdapter.predictUser(req);
    }
    try {
      const response = await apiClient.post<PredictResponse>('/predict', req);
      return response.data;
    } catch {
      console.warn('[userService] FastAPI /predict unavailable, falling back to mock adapter.');
      return mockAdapter.predictUser(req);
    }
  },
};
