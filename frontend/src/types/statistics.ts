export interface NetworkOverviewStats {
  density?: number;
  average_degree?: number;
  average_clustering?: number;
  connected_components?: number;
  diameter?: number;
  modularity?: number;
  transitivity?: number;
}

export interface OverviewStatistics {
  total_users: number;
  total_relationships: number;
  bot_count: number;
  human_count: number;
  bot_ratio: number;
  community_count: number;
  flagged_groups_count?: number;
  network?: NetworkOverviewStats;
  relationship_breakdown?: {
    type: string;
    count: number;
    percentage: number;
  }[];
  community_size_distribution?: {
    size_range: string;
    community_count: number;
  }[];
  system_insights?: string[];
}
