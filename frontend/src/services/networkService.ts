import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { NetworkGraphData, NetworkFilterOptions } from '../types/network';
import { normalizeGraphData } from '../utils/graphNormalizer';

export { normalizeGraphData };

export const networkService = {
  async getNetwork(filters?: Partial<NetworkFilterOptions>): Promise<NetworkGraphData> {
    if (FORCE_MOCK) {
      const mockData = await mockAdapter.getNetwork(filters);
      return normalizeGraphData(mockData);
    }

    const params: Record<string, any> = {
      max_nodes: Math.min(filters?.maxNodes || 100, 200),
      max_edges: 350,
      min_degree: filters?.minDegree || 0,
    };

    if (filters?.relationshipType && filters.relationshipType !== 'ALL') {
      params.relationship_type = filters.relationshipType;
    }
    if (filters?.communityId && filters.communityId !== 'ALL') {
      params.community_id = filters.communityId;
    }
    if (filters?.prediction && filters.prediction !== 'ALL') {
      params.prediction = filters.prediction;
    }
    if (filters?.searchQuery && filters.searchQuery.trim()) {
      params.search_query = filters.searchQuery.trim();
    }

    try {
      const response = await apiClient.get<NetworkGraphData>('/network', { params });
      return normalizeGraphData(response.data);
    } catch {
      console.warn('[networkService] FastAPI /network unavailable, falling back to mock adapter.');
      const mockData = await mockAdapter.getNetwork(filters);
      return normalizeGraphData(mockData);
    }
  },

  async getSubgraph(seedUserId: string, depth = 1): Promise<NetworkGraphData> {
    if (FORCE_MOCK) {
      const mockData = await mockAdapter.getUserNetwork(seedUserId);
      return normalizeGraphData(mockData);
    }

    try {
      const response = await apiClient.get<NetworkGraphData>(`/network/subgraph`, {
        params: { seed_user_id: seedUserId, depth },
      });
      return normalizeGraphData(response.data);
    } catch {
      console.warn(`[networkService] FastAPI /network/subgraph unavailable, falling back to mock adapter.`);
      const mockData = await mockAdapter.getUserNetwork(seedUserId);
      return normalizeGraphData(mockData);
    }
  },
};
