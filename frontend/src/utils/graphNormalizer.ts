import type { NetworkGraphData } from '../types/network';

/**
 * Normalizes backend network graph payloads to match frontend Cytoscape types.
 * Enforces strict safety limits (max 200 nodes, max 400 edges) to guarantee
 * that Cytoscape.js layouts never block the browser main UI thread.
 */
export function normalizeGraphData(raw: any): NetworkGraphData {
  if (!raw) {
    return { nodes: [], edges: [], metadata: { total_nodes: 0, total_edges: 0 } };
  }

  const rawNodes = Array.isArray(raw.nodes) ? raw.nodes : [];
  const rawEdges = Array.isArray(raw.edges) ? raw.edges : [];

  // Defensive capping: max 200 nodes
  const boundedNodes = rawNodes.slice(0, 200).map((n: any) => {
    const strId = String(n.id);
    let pred = n.prediction;
    if (!pred) {
      if (n.bot_label === 1) pred = 'BOT';
      else if (n.bot_label === 0) pred = 'HUMAN';
      else pred = 'UNKNOWN';
    }
    return {
      id: strId,
      label: n.label || `User ${strId}`,
      screen_name: n.screen_name,
      prediction: pred,
      probability: n.probability,
      community_id: n.community_id !== undefined ? String(n.community_id) : undefined,
      degree: typeof n.degree === 'number' ? n.degree : 0,
      pagerank: typeof n.pagerank === 'number' ? n.pagerank : 0.001,
      clustering: n.clustering,
      is_seed: Boolean(n.is_seed),
    };
  });

  const validNodeIds = new Set(boundedNodes.map((n: { id: string }) => n.id));

  // Defensive capping: max 400 edges, only between valid rendered nodes
  const boundedEdges = rawEdges
    .filter((e: any) => validNodeIds.has(String(e.source)) && validNodeIds.has(String(e.target)))
    .slice(0, 400)
    .map((e: any, idx: number) => {
      const src = String(e.source);
      const tgt = String(e.target);
      const rel = (e.relationship || e.relationship_type || 'interaction').toUpperCase();
      return {
        id: e.id || `e-${src}-${tgt}-${idx}`,
        source: src,
        target: tgt,
        relationship: rel,
        weight: typeof e.weight === 'number' ? e.weight : 1.0,
      };
    });

  return {
    nodes: boundedNodes,
    edges: boundedEdges,
    metadata: {
      total_nodes: raw.metadata?.total_nodes ?? raw.node_count ?? boundedNodes.length,
      total_edges: raw.metadata?.total_edges ?? raw.edge_count ?? boundedEdges.length,
      subgraph_type: raw.metadata?.subgraph_type,
      seed_node: raw.metadata?.seed_node ? String(raw.metadata.seed_node) : undefined,
      is_filtered: raw.metadata?.is_filtered ?? true,
    },
  };
}
