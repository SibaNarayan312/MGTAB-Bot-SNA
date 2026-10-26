import {
  MOCK_STATISTICS,
  MOCK_USERS,
  MOCK_NETWORK_GRAPH,
  MOCK_COMMUNITIES,
  MOCK_COMMUNITY_DETAILS,
  MOCK_COORDINATION,
  MOCK_MODEL_PERFORMANCE,
} from './mockData';
import { OverviewStatistics } from '../types/statistics';
import { UserProfile, PredictRequest, PredictResponse } from '../types/user';
import { NetworkGraphData, NetworkFilterOptions } from '../types/network';
import { CommunitiesResponse, CommunityDetails } from '../types/community';
import { CoordinationSummaryResponse } from '../types/coordination';
import { ModelPerformanceResponse } from '../types/model';

// Simulated latency helper
const delay = (ms = 250) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockAdapter = {
  async getStatistics(): Promise<OverviewStatistics> {
    await delay(200);
    return JSON.parse(JSON.stringify(MOCK_STATISTICS));
  },

  async getUser(userId: string): Promise<UserProfile> {
    await delay(300);
    const user = MOCK_USERS[userId];
    if (user) {
      return JSON.parse(JSON.stringify(user));
    }
    // Generate synthetic response for any other requested user ID in mock mode
    return {
      user_id: userId,
      screen_name: `user_${userId.slice(-4)}`,
      name: `User #${userId}`,
      prediction: Number(userId.slice(-1)) % 2 === 0 ? 'BOT' : 'HUMAN',
      probability: Number(userId.slice(-1)) % 2 === 0 ? 0.88 : 0.12,
      confidence_score: 0.91,
      community_id: String((Number(userId.slice(-2)) % 48) + 1),
      features: {
        followers_count: 540,
        following_count: 1200,
        statuses_count: 8500,
        favourites_count: 420,
        verified: false,
        account_age_days: 450,
      },
      network: {
        degree: 42,
        in_degree: 12,
        out_degree: 30,
        pagerank: 0.0024,
        betweenness: 0.015,
        clustering: 0.14,
      },
      explanation: [
        {
          feature: 'GNN Node Representation',
          importance: 0.72,
          description: 'High embedding similarity to known coordinated bot clusters',
          direction: 'positive',
        },
      ],
    };
  },

  async getUserNetwork(userId: string): Promise<NetworkGraphData> {
    await delay(350);
    const allGraph = JSON.parse(JSON.stringify(MOCK_NETWORK_GRAPH)) as NetworkGraphData;
    // If seed exists in mock, filter neighborhood
    const userNode = allGraph.nodes.find((n) => n.id === userId);
    if (!userNode) {
      // Create seed node + 3 neighbors
      const generatedNodes = [
        { id: userId, label: `User ${userId}`, prediction: 'BOT' as const, probability: 0.85, community_id: '17', is_seed: true },
        { id: '123456789', label: 'Tech Trend Echo', prediction: 'BOT' as const, probability: 0.934, community_id: '17' },
        { id: '555123999', label: 'News Radar Bot', prediction: 'BOT' as const, probability: 0.892, community_id: '17' },
      ];
      const generatedEdges = [
        { id: `gen-e1`, source: userId, target: '123456789', relationship: 'RETWEET', weight: 3.5 },
        { id: `gen-e2`, source: userId, target: '555123999', relationship: 'FOLLOW', weight: 1.0 },
      ];
      return {
        nodes: generatedNodes,
        edges: generatedEdges,
        metadata: { total_nodes: generatedNodes.length, total_edges: generatedEdges.length, seed_node: userId },
      };
    }

    const connectedEdges = allGraph.edges.filter((e) => e.source === userId || e.target === userId);
    const connectedNodeIds = new Set<string>([userId]);
    connectedEdges.forEach((e) => {
      connectedNodeIds.add(e.source);
      connectedNodeIds.add(e.target);
    });

    const neighborhoodNodes = allGraph.nodes
      .filter((n) => connectedNodeIds.has(n.id))
      .map((n) => ({ ...n, is_seed: n.id === userId }));

    return {
      nodes: neighborhoodNodes,
      edges: connectedEdges,
      metadata: {
        total_nodes: neighborhoodNodes.length,
        total_edges: connectedEdges.length,
        seed_node: userId,
      },
    };
  },

  async getNetwork(filters?: Partial<NetworkFilterOptions>): Promise<NetworkGraphData> {
    await delay(300);
    let graph = JSON.parse(JSON.stringify(MOCK_NETWORK_GRAPH)) as NetworkGraphData;

    if (filters) {
      if (filters.prediction && filters.prediction !== 'ALL') {
        const allowedIds = new Set(
          graph.nodes.filter((n) => n.prediction === filters.prediction).map((n) => n.id)
        );
        graph.nodes = graph.nodes.filter((n) => allowedIds.has(n.id));
        graph.edges = graph.edges.filter((e) => allowedIds.has(e.source) && allowedIds.has(e.target));
      }

      if (filters.communityId && filters.communityId !== 'ALL') {
        const commIds = new Set(
          graph.nodes.filter((n) => String(n.community_id) === String(filters.communityId)).map((n) => n.id)
        );
        graph.nodes = graph.nodes.filter((n) => commIds.has(n.id));
        graph.edges = graph.edges.filter((e) => commIds.has(e.source) && commIds.has(e.target));
      }

      if (filters.relationshipType && filters.relationshipType !== 'ALL') {
        graph.edges = graph.edges.filter((e) => e.relationship === filters.relationshipType);
      }

      if (filters.minDegree !== undefined && filters.minDegree > 0) {
        const highDegreeIds = new Set(
          graph.nodes.filter((n) => (n.degree || 0) >= (filters.minDegree || 0)).map((n) => n.id)
        );
        graph.nodes = graph.nodes.filter((n) => highDegreeIds.has(n.id));
        graph.edges = graph.edges.filter((e) => highDegreeIds.has(e.source) && highDegreeIds.has(e.target));
      }

      if (filters.searchQuery && filters.searchQuery.trim() !== '') {
        const q = filters.searchQuery.toLowerCase();
        const matchedIds = new Set(
          graph.nodes
            .filter((n) => n.id.includes(q) || (n.label && n.label.toLowerCase().includes(q)) || (n.screen_name && n.screen_name.toLowerCase().includes(q)))
            .map((n) => n.id)
        );
        graph.nodes = graph.nodes.filter((n) => matchedIds.has(n.id));
        graph.edges = graph.edges.filter((e) => matchedIds.has(e.source) && matchedIds.has(e.target));
      }
    }

    return graph;
  },

  async getCommunities(): Promise<CommunitiesResponse> {
    await delay(250);
    return JSON.parse(JSON.stringify(MOCK_COMMUNITIES));
  },

  async getCommunityDetails(communityId: string | number): Promise<CommunityDetails> {
    await delay(250);
    const key = String(communityId);
    if (MOCK_COMMUNITY_DETAILS[key]) {
      return JSON.parse(JSON.stringify(MOCK_COMMUNITY_DETAILS[key]));
    }
    const foundSummary = MOCK_COMMUNITIES.communities.find((c) => String(c.id) === key);
    return {
      id: key,
      member_count: foundSummary?.member_count || 32,
      bot_count: foundSummary?.bot_count || 12,
      human_count: (foundSummary?.member_count || 32) - (foundSummary?.bot_count || 12),
      bot_ratio: foundSummary?.bot_ratio || 0.375,
      coordination_score: foundSummary?.coordination_score || 0.45,
      status: foundSummary?.status || 'moderate_risk',
      primary_topics: foundSummary?.primary_topics || ['General Engagement'],
      density: 0.045,
      average_degree: 16.2,
      signals: [
        {
          signal: 'Multi-Relational Graph Density',
          score: 0.72,
          description: 'Community network modularity and interaction score',
        },
      ],
      network_statistics: {
        internal_edges: 180,
        external_edges: 40,
        conductance: 0.18,
        modularity_contribution: 0.04,
        clustering_coefficient: 0.32,
        density: 0.045,
      },
      members: [
        { user_id: `${key}001`, screen_name: `member_${key}_1`, prediction: 'BOT', probability: 0.89, degree: 45, pagerank: 0.002 },
        { user_id: `${key}002`, screen_name: `member_${key}_2`, prediction: 'HUMAN', probability: 0.14, degree: 38, pagerank: 0.003 },
      ],
    };
  },

  async getCoordination(): Promise<CoordinationSummaryResponse> {
    await delay(250);
    return JSON.parse(JSON.stringify(MOCK_COORDINATION));
  },

  async getModelPerformance(): Promise<ModelPerformanceResponse> {
    await delay(250);
    return JSON.parse(JSON.stringify(MOCK_MODEL_PERFORMANCE));
  },

  async predictUser(req: PredictRequest): Promise<PredictResponse> {
    await delay(400);
    const userIdStr = String(req.user_id || '0');
    const userIdNum = parseInt(userIdStr, 10) || 0;
    const isBot = userIdStr.includes('bot') || Number(userIdStr.slice(-1)) % 2 === 0;
    return {
      status: 'success',
      message: 'ML prediction executed successfully (Mock).',
      user_id: userIdNum,
      prediction: isBot ? 1 : 0,
      prediction_label: isBot ? 'BOT' : 'HUMAN',
      probability: isBot ? 0.924 : 0.078,
      confidence: 0.95,
      explanation: [
        {
          feature: 'SNA Degree Centrality',
          importance: 0.82,
          description: 'High connectivity with suspicious neighborhoods (HistGradientBoosting feature)',
          direction: 'positive',
        },
        {
          feature: 'Profile Feature Ratio',
          importance: 0.74,
          description: 'Account metadata patterns consistent with automated behaviour',
          direction: 'positive',
        },
      ],
    };
  },
};
