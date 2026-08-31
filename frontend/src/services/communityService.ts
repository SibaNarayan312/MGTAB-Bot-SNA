import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { CommunitiesResponse, CommunityDetails } from '../types/community';

export const communityService = {
  async getCommunities(): Promise<CommunitiesResponse> {
    if (FORCE_MOCK) {
      return mockAdapter.getCommunities();
    }
    try {
      const response = await apiClient.get<CommunitiesResponse>('/communities');
      return response.data;
    } catch {
      console.warn('[communityService] FastAPI /communities unavailable, falling back to mock adapter.');
      return mockAdapter.getCommunities();
    }
  },

  async getCommunityDetails(communityId: string | number): Promise<CommunityDetails> {
    if (FORCE_MOCK) {
      return mockAdapter.getCommunityDetails(communityId);
    }
    try {
      const response = await apiClient.get<CommunityDetails>(`/community/${communityId}`);
      return response.data;
    } catch {
      console.warn(`[communityService] FastAPI /community/${communityId} unavailable, falling back to mock adapter.`);
      return mockAdapter.getCommunityDetails(communityId);
    }
  },
};
