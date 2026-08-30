export type CommunityRiskStatus = 
  | 'potentially_coordinated' 
  | 'bot_heavy' 
  | 'moderate_risk' 
  | 'low_risk' 
  | 'unclassified';

export interface CommunitySummary {
  id: string | number;
  member_count: number;
  bot_count: number;
  human_count?: number;
  bot_ratio: number;
  coordination_score?: number;
  status: CommunityRiskStatus;
  primary_topics?: string[];
  density?: number;
  average_degree?: number;
  top_active_users?: string[];
}

export interface CommunityDetails extends CommunitySummary {
  signals?: {
    signal: string;
    score?: number;
    description?: string;
  }[];
  network_statistics?: {
    internal_edges?: number;
    external_edges?: number;
    conductance?: number;
    modularity_contribution?: number;
    clustering_coefficient?: number;
    density?: number;
  };
  members?: {
    user_id: string;
    screen_name?: string;
    prediction?: 'BOT' | 'HUMAN' | 'UNKNOWN';
    probability?: number;
    degree?: number;
    pagerank?: number;
  }[];
  temporal_activity?: {
    time_bucket: string;
    action_count: number;
  }[];
}

export interface CommunitiesResponse {
  total_communities: number;
  communities: CommunitySummary[];
  overall_stats?: {
    largest_community_size?: number;
    average_community_size?: number;
    flagged_communities_count?: number;
  };
}
