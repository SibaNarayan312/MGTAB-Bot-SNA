export interface CoordinationSignal {
  signal: string;
  score?: number;
  description?: string;
  category?: 'temporal' | 'semantic' | 'topological' | 'behavioral';
}

export interface CoordinatedGroup {
  group_id: string | number;
  community_id: string | number;
  member_count: number;
  bot_count: number;
  bot_ratio: number;
  coordination_score: number;
  status: string;
  primary_topic?: string;
  detected_at?: string;
  signals: CoordinationSignal[];
  shared_entities?: {
    urls?: { url: string; count: number }[];
    hashtags?: { tag: string; count: number }[];
    target_accounts?: { target: string; count: number }[];
  };
  temporal_burst_score?: number;
  subgraph_density?: number;
}

export interface CoordinationSummaryResponse {
  total_flagged_groups: number;
  average_coordination_score: number;
  top_coordination_signals: { signal: string; frequency: number }[];
  groups: CoordinatedGroup[];
}
