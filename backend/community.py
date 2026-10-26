import logging
from typing import Dict, Any, List, Tuple, Optional
import networkx as nx
from backend.config import COMMUNITY_CONFIG
from backend.graph_builder import MGTABGraphLoader

logger = logging.getLogger(__name__)

class CommunityDetector:
    """
    Community Detection Engine for MGTAB multi-relational graphs.
    Projects MultiDiGraph into a weighted undirected graph and detects communities
    using Louvain, Leiden, or Connected Component methods.
    """

    def __init__(self, loader: MGTABGraphLoader, config: Optional[Dict[str, Any]] = None):
        self.loader = loader
        self.config = config or COMMUNITY_CONFIG
        self.multigraph: nx.MultiDiGraph = self.loader.build_multidigraph()
        
        self.projected_graph: Optional[nx.Graph] = None
        self.node_community_map: Dict[int, int] = {}
        self.community_stats: Dict[int, Dict[str, Any]] = {}

    def prepare_community_graph(self) -> nx.Graph:
        """
        Transforms MultiDiGraph into a simple weighted undirected graph
        by aggregating weights across all directed multi-relational interactions.
        """
        logger.info("Projecting MultiDiGraph into weighted undirected graph for community detection...")
        G_undirected = nx.Graph()
        G_undirected.add_nodes_from(self.multigraph.nodes())

        for u, v, data in self.multigraph.edges(data=True):
            if u == v:
                continue  # ignore self-loops in community projection
            w = data.get("weight", 1.0)
            if G_undirected.has_edge(u, v):
                G_undirected[u][v]["weight"] += w
            else:
                G_undirected.add_edge(u, v, weight=w)

        self.projected_graph = G_undirected
        return G_undirected

    def detect_communities(self) -> Dict[int, int]:
        """
        Runs community detection algorithm (Louvain / Component propagation).
        Returns node_id -> community_id mapping.
        """
        if self.projected_graph is None:
            self.prepare_community_graph()

        G = self.projected_graph
        method = self.config.get("method", "louvain").lower()
        resolution = self.config.get("resolution", 1.0)
        seed = self.config.get("random_state", 42)

        logger.info(f"Detecting communities using method: '{method}' (resolution={resolution})...")

        communities_list: List[set] = []

        if method == "louvain":
            try:
                communities_list = list(nx.community.louvain_communities(G, weight="weight", resolution=resolution, seed=seed))
            except Exception as e:
                logger.warning(f"Louvain failed ({e}), falling back to greedy modularity.")
                communities_list = list(nx.community.greedy_modularity_communities(G, weight="weight"))
        elif method == "label_propagation":
            try:
                communities_list = list(nx.community.label_propagation_communities(G))
            except Exception as e:
                logger.warning(f"Label propagation failed ({e}), falling back to connected components.")
                communities_list = [set(c) for c in nx.connected_components(G)]
        else:
            # Fallback to connected components
            communities_list = [set(c) for c in nx.connected_components(G)]

        # Sort communities by size descending
        communities_list.sort(key=len, reverse=True)

        node_map = {}
        for comm_id, node_set in enumerate(communities_list):
            for n in node_set:
                node_map[n] = comm_id

        self.node_community_map = node_map
        logger.info(f"Detected {len(communities_list)} communities across {len(node_map)} nodes.")
        return node_map

    def calculate_community_statistics(
        self,
        pagerank_dict: Optional[Dict[int, float]] = None
    ) -> Dict[int, Dict[str, Any]]:
        """
        Calculates per-community metrics:
        - community_id, size
        - internal_edges, external_edges, density
        - top_nodes (sorted by PageRank/degree)
        - relationship_distribution
        """
        if self.community_stats and not pagerank_dict:
            return self.community_stats

        if not self.node_community_map:
            self.detect_communities()

        logger.info("Computing detailed community statistics...")
        
        # Group nodes by community
        comm_nodes: Dict[int, List[int]] = {}
        for n, c_id in self.node_community_map.items():
            comm_nodes.setdefault(c_id, []).append(n)

        stats = {}
        multigraph = self.multigraph

        for c_id, nodes in comm_nodes.items():
            node_set = set(nodes)
            size = len(nodes)

            internal_edges = 0
            external_edges = 0
            rel_distribution: Dict[str, int] = {}

            # Analyze multi-relational edges
            for u in nodes:
                for _, v, data in multigraph.out_edges(u, data=True):
                    rel_name = data.get("relationship_type", "unknown")
                    if v in node_set:
                        internal_edges += 1
                        rel_distribution[rel_name] = rel_distribution.get(rel_name, 0) + 1
                    else:
                        external_edges += 1

            # Internal density
            density = (internal_edges / (size * (size - 1))) if size > 1 else 0.0

            # Top nodes in community by PageRank or degree
            if pagerank_dict:
                top_nodes = sorted(nodes, key=lambda n: pagerank_dict.get(n, 0.0), reverse=True)[:5]
            else:
                top_nodes = sorted(nodes, key=lambda n: multigraph.degree(n), reverse=True)[:5]

            stats[c_id] = {
                "community_id": c_id,
                "size": size,
                "internal_edges": internal_edges,
                "external_edges": external_edges,
                "density": float(density),
                "top_nodes": top_nodes,
                "relationship_distribution": rel_distribution,
            }

        self.community_stats = stats
        return stats

    def get_community_members(self, community_id: int) -> List[int]:
        """Returns list of node IDs belonging to community_id."""
        if not self.node_community_map:
            self.detect_communities()
        return [n for n, c_id in self.node_community_map.items() if c_id == community_id]
