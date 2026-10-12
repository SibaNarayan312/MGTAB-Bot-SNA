import { OverviewStatistics } from '../types/statistics';
import { UserProfile } from '../types/user';
import { NetworkGraphData } from '../types/network';
import { CommunityDetails, CommunitiesResponse } from '../types/community';
import { CoordinationSummaryResponse } from '../types/coordination';
import { ModelPerformanceResponse } from '../types/model';

// Overview Statistics based on MGTAB benchmark structure
export const MOCK_STATISTICS: OverviewStatistics = {
  total_users: 10199,
  total_relationships: 147820,
  bot_count: 2768,
  human_count: 7431,
  bot_ratio: 0.2714,
  community_count: 48,
  flagged_groups_count: 7,
  network: {
    density: 0.00284,
    average_degree: 28.98,
    average_clustering: 0.231,
    connected_components: 12,
    diameter: 8,
    modularity: 0.684,
    transitivity: 0.187,
  },
  relationship_breakdown: [
    { type: 'FOLLOW', count: 72410, percentage: 48.98 },
    { type: 'FRIEND', count: 41200, percentage: 27.87 },
    { type: 'RETWEET', count: 18450, percentage: 12.48 },
    { type: 'MENTION', count: 11200, percentage: 7.58 },
    { type: 'REPLY', count: 4560, percentage: 3.09 },
  ],
  community_size_distribution: [
    { size_range: '1-25 members', community_count: 14 },
    { size_range: '26-100 members', community_count: 19 },
    { size_range: '101-500 members', community_count: 11 },
    { size_range: '500+ members', community_count: 4 },
  ],
  system_insights: [
    'Graph density of 0.00284 with 10,199 active nodes and 147,820 multi-relational edges in MGTAB benchmark.',
    'Identified 7 communities with elevated coordination scores (>0.75) exhibiting synchronous retweeting and mention patterns.',
    '2-layer RGCN (RGCNConv, 7 relation types) achieved 85.78% test accuracy with 0.9415 ROC-AUC. HistGradientBoosting baseline: 93.77% accuracy.',
  ],
};

// Rich Mock Users
export const MOCK_USERS: Record<string, UserProfile> = {
  '123456789': {
    user_id: '123456789',
    screen_name: 'bot_alpha_node',
    name: 'Tech Trend Echo',
    prediction: 'BOT',
    probability: 0.934,
    confidence_score: 0.96,
    community_id: '17',
    features: {
      followers_count: 320,
      following_count: 4890,
      statuses_count: 48200,
      favourites_count: 12,
      listed_count: 1,
      created_at: '2023-11-04T12:00:00Z',
      verified: false,
      default_profile: true,
      default_profile_image: true,
      geo_enabled: false,
      account_age_days: 280,
      tweet_frequency_per_day: 172.1,
    },
    network: {
      degree: 148,
      in_degree: 14,
      out_degree: 134,
      pagerank: 0.00482,
      betweenness: 0.0381,
      clustering: 0.042,
      eigenvector: 0.0019,
      coreness: 8,
    },
    explanation: [
      {
        feature: 'Following/Follower Asymmetry',
        importance: 0.88,
        description: 'Disproportionately high following-to-follower ratio (15.28x)',
        direction: 'positive',
      },
      {
        feature: 'High Multi-Relational Out-Degree',
        importance: 0.76,
        description: 'Excessive outgoing retweets and mentions within short time intervals',
        direction: 'positive',
      },
      {
        feature: 'Default Profile Metadata',
        importance: 0.65,
        description: 'Unmodified default avatar and empty user biography',
        direction: 'positive',
      },
      {
        feature: 'Low Local Clustering Coefficient',
        importance: 0.52,
        description: 'Low triad closure indicating broadcast-like network position',
        direction: 'positive',
      },
    ],
    recent_activity: {
      total_tweets_sampled: 500,
      hashtags: ['#BreakingNews', '#CryptoAirdrop', '#TrendingNow', '#ViralAlert'],
      mentioned_users: ['987654321', '456789123', '234567890'],
      urls_shared: ['https://t.co/short8923a', 'https://t.co/alert991x'],
    },
  },
  '987654321': {
    user_id: '987654321',
    screen_name: 'dr_sarah_research',
    name: 'Dr. Sarah Mitchell',
    prediction: 'HUMAN',
    probability: 0.062,
    confidence_score: 0.98,
    community_id: '4',
    features: {
      followers_count: 14500,
      following_count: 820,
      statuses_count: 3200,
      favourites_count: 8940,
      listed_count: 142,
      created_at: '2016-03-15T08:30:00Z',
      verified: true,
      default_profile: false,
      default_profile_image: false,
      geo_enabled: true,
      account_age_days: 3450,
      tweet_frequency_per_day: 0.92,
    },
    network: {
      degree: 284,
      in_degree: 240,
      out_degree: 44,
      pagerank: 0.0289,
      betweenness: 0.0842,
      clustering: 0.384,
      eigenvector: 0.041,
      coreness: 24,
    },
    explanation: [
      {
        feature: 'High Local Clustering',
        importance: 0.84,
        description: 'High triangle closure with reciprocal academic and domain contacts',
        direction: 'negative',
      },
      {
        feature: 'Long Account Longevity',
        importance: 0.79,
        description: 'Account created in 2016 with consistent, organic posting history',
        direction: 'negative',
      },
      {
        feature: 'Reciprocal Follower Ratio',
        importance: 0.72,
        description: 'High inward citation/follow ratio with verified credentials',
        direction: 'negative',
      },
    ],
    recent_activity: {
      total_tweets_sampled: 120,
      hashtags: ['#NetworkScience', '#DataEthics', '#ICWSM2026'],
      mentioned_users: ['345678901', '890123456'],
      urls_shared: ['https://arxiv.org/abs/2401.12345'],
    },
  },
  '555123999': {
    user_id: '555123999',
    screen_name: 'retweet_hub_09',
    name: 'News Radar Bot',
    prediction: 'BOT',
    probability: 0.892,
    confidence_score: 0.92,
    community_id: '17',
    features: {
      followers_count: 42,
      following_count: 2100,
      statuses_count: 67300,
      favourites_count: 4,
      listed_count: 0,
      created_at: '2024-01-10T15:00:00Z',
      verified: false,
      default_profile: true,
      default_profile_image: true,
      geo_enabled: false,
      account_age_days: 190,
      tweet_frequency_per_day: 354.2,
    },
    network: {
      degree: 98,
      in_degree: 4,
      out_degree: 94,
      pagerank: 0.0019,
      betweenness: 0.012,
      clustering: 0.018,
      eigenvector: 0.0008,
      coreness: 5,
    },
    explanation: [
      {
        feature: 'Extreme Tweet Cadence',
        importance: 0.94,
        description: 'Over 350 automated status distributions per day',
        direction: 'positive',
      },
      {
        feature: 'High Retweet-to-Follow Ratio',
        importance: 0.81,
        description: 'Disproportionately high retweet interactions compared to follow connections',
        direction: 'positive',
      },
    ],
  },
};

// Full / Subgraph Mock Network with diverse nodes and multi-relational edges
export const MOCK_NETWORK_GRAPH: NetworkGraphData = {
  nodes: [
    // Community 17 - Flagged / Coordinated cluster
    { id: '123456789', label: 'Tech Trend Echo', prediction: 'BOT', probability: 0.934, community_id: '17', degree: 148, pagerank: 0.00482, screen_name: 'bot_alpha_node', is_seed: true },
    { id: '555123999', label: 'News Radar Bot', prediction: 'BOT', probability: 0.892, community_id: '17', degree: 98, pagerank: 0.0019, screen_name: 'retweet_hub_09' },
    { id: '555123888', label: 'Trend Amplifier 01', prediction: 'BOT', probability: 0.915, community_id: '17', degree: 84, pagerank: 0.0016, screen_name: 'amplify_01' },
    { id: '555123777', label: 'Trend Amplifier 02', prediction: 'BOT', probability: 0.879, community_id: '17', degree: 76, pagerank: 0.0014, screen_name: 'amplify_02' },
    { id: '555123666', label: 'Sync Echo Node', prediction: 'BOT', probability: 0.941, community_id: '17', degree: 92, pagerank: 0.0021, screen_name: 'echo_sync' },
    { id: '555123555', label: 'Bridge Propagator', prediction: 'BOT', probability: 0.782, community_id: '17', degree: 112, pagerank: 0.0035, screen_name: 'bridge_prop' },
    { id: '555123444', label: 'Target Infiltrator', prediction: 'BOT', probability: 0.824, community_id: '17', degree: 64, pagerank: 0.0012, screen_name: 'target_inf' },

    // Community 4 - Organic Research Community
    { id: '987654321', label: 'Dr. Sarah Mitchell', prediction: 'HUMAN', probability: 0.062, community_id: '4', degree: 284, pagerank: 0.0289, screen_name: 'dr_sarah_research', is_seed: true },
    { id: '345678901', label: 'Prof. Alex Chen', prediction: 'HUMAN', probability: 0.041, community_id: '4', degree: 195, pagerank: 0.0194, screen_name: 'prof_alex_c' },
    { id: '890123456', label: 'NetSci Lab', prediction: 'HUMAN', probability: 0.098, community_id: '4', degree: 160, pagerank: 0.0152, screen_name: 'netsci_official' },
    { id: '789012345', label: 'Elena Rostova', prediction: 'HUMAN', probability: 0.082, community_id: '4', degree: 130, pagerank: 0.0112, screen_name: 'elena_phd' },
    { id: '678901234', label: 'David Kim', prediction: 'HUMAN', probability: 0.124, community_id: '4', degree: 94, pagerank: 0.0084, screen_name: 'dkim_soc' },

    // Community 9 - Media & Journalism
    { id: '456789123', label: 'Global News Feed', prediction: 'HUMAN', probability: 0.185, community_id: '9', degree: 310, pagerank: 0.0341, screen_name: 'globalnews_live' },
    { id: '234567890', label: 'Press Bureau', prediction: 'HUMAN', probability: 0.221, community_id: '9', degree: 215, pagerank: 0.0210, screen_name: 'press_desk' },
    { id: '112233445', label: 'Anchor Journalist', prediction: 'HUMAN', probability: 0.054, community_id: '9', degree: 145, pagerank: 0.0142, screen_name: 'anchor_j' },

    // Community 22 - Suspicious Airdrop Botnet
    { id: '998877661', label: 'Crypto Claimer 1', prediction: 'BOT', probability: 0.952, community_id: '22', degree: 78, pagerank: 0.0018, screen_name: 'claim_bot1' },
    { id: '998877662', label: 'Crypto Claimer 2', prediction: 'BOT', probability: 0.961, community_id: '22', degree: 82, pagerank: 0.0019, screen_name: 'claim_bot2' },
    { id: '998877663', label: 'Crypto Claimer 3', prediction: 'BOT', probability: 0.948, community_id: '22', degree: 75, pagerank: 0.0017, screen_name: 'claim_bot3' },
    { id: '998877664', label: 'Crypto Hub Relay', prediction: 'BOT', probability: 0.982, community_id: '22', degree: 120, pagerank: 0.0041, screen_name: 'airdrop_hub' },
  ],
  edges: [
    // Internal Community 17 coordinated edges
    { id: 'e1', source: '123456789', target: '555123999', relationship: 'RETWEET', weight: 4.5 },
    { id: 'e2', source: '123456789', target: '555123888', relationship: 'RETWEET', weight: 4.8 },
    { id: 'e3', source: '555123999', target: '555123777', relationship: 'RETWEET', weight: 3.9 },
    { id: 'e4', source: '555123888', target: '555123666', relationship: 'MENTION', weight: 2.5 },
    { id: 'e5', source: '555123777', target: '555123666', relationship: 'RETWEET', weight: 5.0 },
    { id: 'e6', source: '555123666', target: '123456789', relationship: 'FOLLOW', weight: 1.0 },
    { id: 'e7', source: '555123555', target: '123456789', relationship: 'FOLLOW', weight: 1.0 },
    { id: 'e8', source: '555123555', target: '555123999', relationship: 'FOLLOW', weight: 1.0 },
    { id: 'e9', source: '555123444', target: '555123888', relationship: 'MENTION', weight: 3.1 },
    { id: 'e10', source: '555123444', target: '555123555', relationship: 'RETWEET', weight: 2.8 },

    // Community 17 brigading/targeting external nodes
    { id: 'e11', source: '555123555', target: '456789123', relationship: 'MENTION', weight: 1.2 },
    { id: 'e12', source: '123456789', target: '456789123', relationship: 'REPLY', weight: 2.0 },
    { id: 'e13', source: '555123444', target: '234567890', relationship: 'MENTION', weight: 1.5 },

    // Community 4 organic reciprocal edges
    { id: 'e14', source: '987654321', target: '345678901', relationship: 'FRIEND', weight: 5.0 },
    { id: 'e15', source: '345678901', target: '987654321', relationship: 'FRIEND', weight: 5.0 },
    { id: 'e16', source: '987654321', target: '890123456', relationship: 'FOLLOW', weight: 2.0 },
    { id: 'e17', source: '890123456', target: '987654321', relationship: 'RETWEET', weight: 3.4 },
    { id: 'e18', source: '789012345', target: '987654321', relationship: 'FOLLOW', weight: 1.0 },
    { id: 'e19', source: '789012345', target: '345678901', relationship: 'MENTION', weight: 2.1 },
    { id: 'e20', source: '678901234', target: '890123456', relationship: 'FRIEND', weight: 3.0 },
    { id: 'e21', source: '678901234', target: '987654321', relationship: 'REPLY', weight: 1.8 },

    // Community 9 Media connections
    { id: 'e22', source: '456789123', target: '234567890', relationship: 'FRIEND', weight: 4.0 },
    { id: 'e23', source: '112233445', target: '456789123', relationship: 'FRIEND', weight: 4.0 },
    { id: 'e24', source: '987654321', target: '456789123', relationship: 'FOLLOW', weight: 1.0 },

    // Community 22 Crypto botnet
    { id: 'e25', source: '998877661', target: '998877664', relationship: 'RETWEET', weight: 5.0 },
    { id: 'e26', source: '998877662', target: '998877664', relationship: 'RETWEET', weight: 5.0 },
    { id: 'e27', source: '998877663', target: '998877664', relationship: 'RETWEET', weight: 4.9 },
    { id: 'e28', source: '998877664', target: '998877661', relationship: 'MENTION', weight: 3.0 },
    { id: 'e29', source: '998877664', target: '998877662', relationship: 'MENTION', weight: 3.0 },
  ],
  metadata: {
    total_nodes: 18,
    total_edges: 29,
    subgraph_type: 'multi_community_sample',
    is_filtered: false,
  },
};

// Communities Mock Dataset
export const MOCK_COMMUNITIES: CommunitiesResponse = {
  total_communities: 48,
  overall_stats: {
    largest_community_size: 1420,
    average_community_size: 212.4,
    flagged_communities_count: 7,
  },
  communities: [
    {
      id: '17',
      member_count: 43,
      bot_count: 31,
      human_count: 12,
      bot_ratio: 0.7209,
      coordination_score: 0.84,
      status: 'potentially_coordinated',
      primary_topics: ['Trending Hashtags', 'News Retweet Echo'],
      density: 0.084,
      average_degree: 18.4,
      top_active_users: ['123456789', '555123999', '555123666'],
    },
    {
      id: '22',
      member_count: 68,
      bot_count: 58,
      human_count: 10,
      bot_ratio: 0.8529,
      coordination_score: 0.91,
      status: 'potentially_coordinated',
      primary_topics: ['Automated Airdrop Spam', 'Token Claims'],
      density: 0.112,
      average_degree: 24.1,
      top_active_users: ['998877664', '998877661', '998877662'],
    },
    {
      id: '4',
      member_count: 1420,
      bot_count: 85,
      human_count: 1335,
      bot_ratio: 0.0598,
      coordination_score: 0.12,
      status: 'low_risk',
      primary_topics: ['Academic Research', 'Network Science', 'Data Mining'],
      density: 0.014,
      average_degree: 32.6,
      top_active_users: ['987654321', '345678901', '890123456'],
    },
    {
      id: '9',
      member_count: 890,
      bot_count: 112,
      human_count: 778,
      bot_ratio: 0.1258,
      coordination_score: 0.24,
      status: 'low_risk',
      primary_topics: ['Journalism', 'Mainstream News', 'Broadcasting'],
      density: 0.021,
      average_degree: 41.2,
      top_active_users: ['456789123', '234567890'],
    },
    {
      id: '31',
      member_count: 125,
      bot_count: 78,
      human_count: 47,
      bot_ratio: 0.624,
      coordination_score: 0.76,
      status: 'potentially_coordinated',
      primary_topics: ['Political Slogan Amplification'],
      density: 0.065,
      average_degree: 14.8,
      top_active_users: ['771122334', '771122335'],
    },
    {
      id: '12',
      member_count: 340,
      bot_count: 145,
      human_count: 195,
      bot_ratio: 0.4264,
      coordination_score: 0.49,
      status: 'moderate_risk',
      primary_topics: ['Entertainment & Fan Engagement'],
      density: 0.038,
      average_degree: 19.1,
      top_active_users: ['441122334'],
    },
  ],
};

// Community Detail Mock
export const MOCK_COMMUNITY_DETAILS: Record<string, CommunityDetails> = {
  '17': {
    id: '17',
    member_count: 43,
    bot_count: 31,
    human_count: 12,
    bot_ratio: 0.7209,
    coordination_score: 0.84,
    status: 'potentially_coordinated',
    primary_topics: ['Trending Hashtags', 'News Retweet Echo'],
    density: 0.084,
    average_degree: 18.4,
    top_active_users: ['123456789', '555123999', '555123666'],
    signals: [
      {
        signal: 'Synchronized Retweet Bursts',
        score: 0.91,
        description: 'Multiple accounts retweeting seed accounts within a 5-second window',
      },
      {
        signal: 'Dense Internal Subgraph Structure',
        score: 0.84,
        description: 'Internal density is 29x higher than expected background graph density',
      },
      {
        signal: 'Shared Shortened URL Patterns',
        score: 0.78,
        description: '92% of links route to recurring external redirection domains',
      },
    ],
    network_statistics: {
      internal_edges: 382,
      external_edges: 49,
      conductance: 0.113,
      modularity_contribution: 0.089,
      clustering_coefficient: 0.442,
      density: 0.084,
    },
    members: [
      { user_id: '123456789', screen_name: 'bot_alpha_node', prediction: 'BOT', probability: 0.934, degree: 148, pagerank: 0.00482 },
      { user_id: '555123999', screen_name: 'retweet_hub_09', prediction: 'BOT', probability: 0.892, degree: 98, pagerank: 0.0019 },
      { user_id: '555123888', screen_name: 'amplify_01', prediction: 'BOT', probability: 0.915, degree: 84, pagerank: 0.0016 },
      { user_id: '555123777', screen_name: 'amplify_02', prediction: 'BOT', probability: 0.879, degree: 76, pagerank: 0.0014 },
      { user_id: '555123666', screen_name: 'echo_sync', prediction: 'BOT', probability: 0.941, degree: 92, pagerank: 0.0021 },
      { user_id: '555123555', screen_name: 'bridge_prop', prediction: 'BOT', probability: 0.782, degree: 112, pagerank: 0.0035 },
    ],
  },
};

// Coordination Analysis Mock Dataset
export const MOCK_COORDINATION: CoordinationSummaryResponse = {
  total_flagged_groups: 7,
  average_coordination_score: 0.824,
  top_coordination_signals: [
    { signal: 'Synchronized Retweet Latency (<5s)', frequency: 6 },
    { signal: 'Repeated Mention Flooding', frequency: 5 },
    { signal: 'Shared URL Domain Co-occurrence', frequency: 4 },
    { signal: 'Near-Identical Profile Creation Dates', frequency: 4 },
    { signal: 'High Internal Subgraph Density', frequency: 7 },
  ],
  groups: [
    {
      group_id: 'GRP-17',
      community_id: '17',
      member_count: 43,
      bot_count: 31,
      bot_ratio: 0.7209,
      coordination_score: 0.84,
      status: 'Potentially Coordinated',
      primary_topic: 'Rapid Retweet Cascades',
      detected_at: '2026-08-20T14:22:00Z',
      temporal_burst_score: 0.89,
      subgraph_density: 0.084,
      signals: [
        {
          signal: 'High Multi-Relational Reciprocity within Cluster',
          score: 0.88,
          description: 'High frequency of reciprocal retweets and reply amplifications',
          category: 'topological',
        },
        {
          signal: 'Synchronous Temporal Action Timestamps',
          score: 0.91,
          description: 'Standard deviation of retweet response latency is under 4.2 seconds',
          category: 'temporal',
        },
        {
          signal: 'Shared URL Redirection Co-occurrence',
          score: 0.76,
          description: 'High overlap of shared shortened tracking URLs',
          category: 'semantic',
        },
      ],
      shared_entities: {
        urls: [
          { url: 'https://t.co/short8923a', count: 184 },
          { url: 'https://t.co/alert991x', count: 142 },
        ],
        hashtags: [
          { tag: '#BreakingNews', count: 320 },
          { tag: '#ViralAlert', count: 215 },
        ],
        target_accounts: [
          { target: '@globalnews_live', count: 78 },
          { target: '@press_desk', count: 54 },
        ],
      },
    },
    {
      group_id: 'GRP-22',
      community_id: '22',
      member_count: 68,
      bot_count: 58,
      bot_ratio: 0.8529,
      coordination_score: 0.91,
      status: 'Potentially Coordinated',
      primary_topic: 'Automated Token Claims',
      detected_at: '2026-08-22T09:15:00Z',
      temporal_burst_score: 0.95,
      subgraph_density: 0.112,
      signals: [
        {
          signal: 'Dense Star-Hub Network Topology',
          score: 0.94,
          description: '58 bot nodes synchronously retweeting single central controller hub node',
          category: 'topological',
        },
        {
          signal: 'Identical Account Creation Waves',
          score: 0.89,
          description: 'Accounts registered in bulk within a 48-hour timeframe',
          category: 'behavioral',
        },
      ],
      shared_entities: {
        urls: [{ url: 'https://claim-airdrop-bonus.xyz', count: 412 }],
        hashtags: [{ tag: '#CryptoAirdrop', count: 540 }, { tag: '#ClaimFree', count: 310 }],
        target_accounts: [{ target: '@airdrop_hub', count: 290 }],
      },
    },
    {
      group_id: 'GRP-31',
      community_id: '31',
      member_count: 125,
      bot_count: 78,
      bot_ratio: 0.624,
      coordination_score: 0.76,
      status: 'Potentially Coordinated',
      primary_topic: 'Political Slogan Amplification',
      detected_at: '2026-08-25T18:40:00Z',
      temporal_burst_score: 0.74,
      subgraph_density: 0.065,
      signals: [
        {
          signal: 'Coordinated Hashtag Hijacking',
          score: 0.81,
          description: 'Spamming common civic hashtags alongside predefined messaging texts',
          category: 'semantic',
        },
      ],
      shared_entities: {
        hashtags: [{ tag: '#CivicDebate2026', count: 480 }, { tag: '#VoteTrend', count: 320 }],
        target_accounts: [{ target: '@civic_forum', count: 92 }],
      },
    },
  ],
};

// Model Performance Mock Dataset
// NOTE: These are ACTUAL results from trained models, not fabricated.
// RGCN results from: results/rgcn_results.json (epoch 24 checkpoint)
// Baseline results from: results/model_comparison.csv
export const MOCK_MODEL_PERFORMANCE: ModelPerformanceResponse = {
  metrics: {
    accuracy: 0.8578,
    precision: 0.6796,
    recall: 0.8945,
    f1_score: 0.7724,
    roc_auc: 0.9415,
  },
  confusion_matrix: {
    true_negative: 629,   // Actual Human, Predicted Human (TN)
    false_positive: 116,  // Actual Human, Predicted Bot (FP)
    false_negative: 29,   // Actual Bot, Predicted Human (FN)
    true_positive: 246,   // Actual Bot, Predicted Bot (TP)
  },
  metadata: {
    model_name: 'RGCN (2-layer RGCNConv)',
    model_version: 'v1.0.0',
    architecture_type: 'Relational Graph Convolutional Network (RGCNConv)',
    dataset_name: 'MGTAB (Multi-relational Graph Twitter Account Benchmark)',
    dataset_version: '1.0',
    training_samples: 8159,
    test_samples: 1020,
    validation_split: '80/10/10 Stratified Node Split',
    evaluation_date: '2026-09-27',
    feature_count: 788,
    graph_layers: 2,
    embedding_dimension: 64,
    epochs_trained: 24,
  },
  roc_curve: [
    { fpr: 0.0, tpr: 0.0 },
    { fpr: 0.05, tpr: 0.70 },
    { fpr: 0.10, tpr: 0.82 },
    { fpr: 0.16, tpr: 0.89 },
    { fpr: 0.30, tpr: 0.95 },
    { fpr: 0.50, tpr: 0.98 },
    { fpr: 1.0, tpr: 1.0 },
  ],
  feature_importances: [
    { feature: 'Profile Features (20 dims)', importance: 0.3767, category: 'user' },
    { feature: 'Text Embeddings (768 dims)', importance: 0.0782, category: 'text' },
    { feature: 'SNA Graph Features (18 dims)', importance: 0.0336, category: 'graph' },
  ],
  baseline_comparisons: [
    { model_name: 'Logistic Regression (806 features)', accuracy: 0.9020, f1_score: 0.8302, roc_auc: 0.9020 },
    { model_name: 'Random Forest (806 features)', accuracy: 0.8961, f1_score: 0.7897, roc_auc: 0.8961 },
    { model_name: 'HistGradientBoosting (806 features)', accuracy: 0.9377, f1_score: 0.8863, roc_auc: 0.9827 },
    { model_name: 'RGCN 2-layer (788 node features, graph)', accuracy: 0.8578, f1_score: 0.7724, roc_auc: 0.9415 },
  ],
};
