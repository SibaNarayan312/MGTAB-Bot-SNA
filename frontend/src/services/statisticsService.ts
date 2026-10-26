import { apiClient, FORCE_MOCK } from './api';
import { mockAdapter } from '../mock/mockAdapter';
import { OverviewStatistics } from '../types/statistics';

function normalizeStatistics(data: any): OverviewStatistics {
  if (!data) return data;
  const totalUsers = data.total_users ?? data.nodes ?? 10199;
  const totalRelationships = data.total_relationships ?? data.edges ?? 1700108;
  const botCount = data.bot_count ?? 2748;
  const humanCount = data.human_count ?? (totalUsers - botCount);
  const botRatio = data.bot_ratio ?? (totalUsers > 0 ? Number((botCount / totalUsers).toFixed(4)) : 0.2694);
  const commCount = data.community_count ?? data.communities ?? 59;

  return {
    ...data,
    total_users: totalUsers,
    total_relationships: totalRelationships,
    bot_count: botCount,
    human_count: humanCount,
    bot_ratio: botRatio,
    community_count: commCount,
  };
}

export const statisticsService = {
  async getOverviewStatistics(): Promise<OverviewStatistics> {
    if (FORCE_MOCK) {
      return mockAdapter.getStatistics();
    }
    try {
      const response = await apiClient.get<OverviewStatistics>('/statistics');
      return normalizeStatistics(response.data);
    } catch {
      console.warn('[statisticsService] FastAPI unavailable, falling back to MGTAB mock data.');
      return mockAdapter.getStatistics();
    }
  },
};
