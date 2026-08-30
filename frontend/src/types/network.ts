import { PredictionLabel, RelationshipType } from './api';

export interface GraphNodeData {
  id: string;
  label?: string;
  prediction?: PredictionLabel;
  probability?: number;
  community_id?: string | number;
  degree?: number;
  pagerank?: number;
  betweenness?: number;
  clustering?: number;
  screen_name?: string;
  is_seed?: boolean;
}

export interface GraphEdgeData {
  id?: string;
  source: string;
  target: string;
  relationship: RelationshipType;
  weight?: number;
  timestamp?: string;
}

export interface CytoscapeNodeElement {
  data: GraphNodeData;
  position?: { x: number; y: number };
  classes?: string;
}

export interface CytoscapeEdgeElement {
  data: GraphEdgeData;
  classes?: string;
}

export type CytoscapeElement = CytoscapeNodeElement | CytoscapeEdgeElement;

export interface NetworkGraphData {
  nodes: GraphNodeData[];
  edges: GraphEdgeData[];
  metadata?: {
    total_nodes?: number;
    total_edges?: number;
    subgraph_type?: string;
    seed_node?: string;
    is_filtered?: boolean;
  };
}

export interface NetworkFilterOptions {
  prediction: 'ALL' | 'BOT' | 'HUMAN' | 'UNKNOWN';
  communityId: string | 'ALL';
  relationshipType: string | 'ALL';
  minDegree: number;
  searchQuery: string;
  maxNodes: number;
}

export type GraphLayoutAlgorithm = 'cose' | 'concentric' | 'circle' | 'breadthfirst' | 'grid';
