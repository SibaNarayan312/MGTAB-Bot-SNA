import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { NetworkGraphData, NetworkFilterOptions } from '../types/network';

export const networkService = {
  async getNetwork(filters?: Partial<NetworkFilterOptions>): Promise<NetworkGraphData> {
    if (FORCE_MOCK) {
      return mockAdapter.getNetwork(filters);
    }
    try {
      const response = await apiClient.get<NetworkGraphData>('/network', {
        params: filters,
      });
      return response.data;
    } catch {
      console.warn('[networkService] FastAPI /network unavailable, falling back to mock adapter.');
      return mockAdapter.getNetwork(filters);
    }
  },

  async getSubgraph(seedUserId: string, depth = 1): Promise<NetworkGraphData> {
    if (FORCE_MOCK) {
      return mockAdapter.getUserNetwork(seedUserId);
    }
    try {
      const response = await apiClient.get<NetworkGraphData>(`/network/subgraph`, {
        params: { seed_user_id: seedUserId, depth },
      });
      return response.data;
    } catch {
      console.warn(`[networkService] FastAPI /network/subgraph unavailable, falling back to mock adapter.`);
      return mockAdapter.getUserNetwork(seedUserId);
    }
  },
};
