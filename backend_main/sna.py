import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import networkx as nx
from backend.config import SNA_CONFIG, RELATIONSHIP_TYPES
from backend.graph_builder import MGTABGraphLoader

logger = logging.getLogger(__name__)

class SNAAnalyzer:
    """
    Social Network Analysis Engine for MGTAB multi-relational graphs.
    Computes node-level metrics, centrality statistics, PageRank, clustering,
    and relationship-specific network indicators.
    """

    def __init__(self, loader: MGTABGraphLoader, config: Optional[Dict[str, Any]] = None):
        self.loader = loader
        self.config = config or SNA_CONFIG
        self.graph: nx.MultiDiGraph = self.loader.build_multidigraph()
        
        self.node_metrics: Dict[int, Dict[str, Any]] = {}
        self.relation_stats: Dict[str, Dict[str, Any]] = {}

    def calculate_node_metrics(self) -> Dict[int, Dict[str, Any]]:
        """
        Calculates node-level SNA metrics for all nodes in the graph:
        - degree, in_degree, out_degree, weighted_degree
        - degree_centrality, pagerank
        - optional approximate betweenness_centrality
        - clustering_coefficient (on converted simple undirected graph)
        """
        logger.info("Computing node-level SNA metrics...")
        G = self.graph
        nodes = list(G.nodes())

        # Initialize storage dict for each node
        metrics = {n: {} for n in nodes}

        # 1. Degree Metrics
        for n in nodes:
            in_deg = G.in_degree(n)
            out_deg = G.out_degree(n)
            tot_deg = in_deg + out_deg

            # Weighted degree (sum of edge weights)
            w_in = sum(d.get("weight", 1.0) for _, _, d in G.in_edges(n, data=True))
            w_out = sum(d.get("weight", 1.0) for _, _, d in G.out_edges(n, data=True))
            
            metrics[n]["degree"] = tot_deg
            metrics[n]["in_degree"] = in_deg
            metrics[n]["out_degree"] = out_deg
            metrics[n]["weighted_degree"] = float(w_in + w_out)

        # 2. Degree Centrality
        num_nodes = len(nodes)
        if num_nodes > 1:
            for n in nodes:
                metrics[n]["degree_centrality"] = metrics[n]["degree"] / (2 * (num_nodes - 1))
        else:
            for n in nodes:
                metrics[n]["degree_centrality"] = 0.0

        # 3. PageRank
        logger.info("Computing PageRank centrality...")
        try:
            # Convert MultiDiGraph to simple DiGraph with aggregated weights for PageRank
            simple_digraph = nx.DiGraph()
            simple_digraph.add_nodes_from(nodes)
            for u, v, data in G.edges(data=True):
                w = data.get("weight", 1.0)
                if simple_digraph.has_edge(u, v):
                    simple_digraph[u][v]["weight"] += w
                else:
                    simple_digraph.add_edge(u, v, weight=w)

            alpha = self.config.get("pagerank_alpha", 0.85)
            max_iter = self.config.get("pagerank_max_iter", 100)
            pr = nx.pagerank(simple_digraph, alpha=alpha, weight="weight", max_iter=max_iter)
            for n in nodes:
                metrics[n]["pagerank"] = float(pr.get(n, 0.0))
        except Exception as e:
            logger.warning(f"PageRank computation failed: {e}. Falling back to default.")
            for n in nodes:
                metrics[n]["pagerank"] = 1.0 / max(num_nodes, 1)

        # 4. Betweenness Centrality (Configurable & Optional)
        compute_betweenness = self.config.get("compute_betweenness", False)
        if compute_betweenness:
            logger.info("Computing approximate Betweenness Centrality...")
            k_samples = min(self.config.get("betweenness_k", 100), num_nodes)
            try:
                btw = nx.betweenness_centrality(G, k=k_samples, normalized=True)
                for n in nodes:
                    metrics[n]["betweenness"] = float(btw.get(n, 0.0))
            except Exception as e:
                logger.warning(f"Betweenness computation failed: {e}")
                for n in nodes:
                    metrics[n]["betweenness"] = 0.0
        else:
            for n in nodes:
                metrics[n]["betweenness"] = 0.0

        # 5. Clustering Coefficient (on simple undirected transformation)
        if self.config.get("compute_clustering", True):
            logger.info("Computing Local Clustering Coefficient...")
            undirected_g = nx.Graph()
            undirected_g.add_nodes_from(nodes)
            for u, v in G.edges():
                if u != v:
                    undirected_g.add_edge(u, v)

            clustering = nx.clustering(undirected_g)
            for n in nodes:
                metrics[n]["clustering_coefficient"] = float(clustering.get(n, 0.0))
        else:
            for n in nodes:
                metrics[n]["clustering_coefficient"] = 0.0

        # 6. Per-relation sub-degrees (mentions, replies, quotes, urls, hashtags, followers, friends)
        for rel_id, rel_name in RELATIONSHIP_TYPES.items():
            deg_key = f"{rel_name}_degree"
            for n in nodes:
                metrics[n][deg_key] = 0

        for u, v, data in G.edges(data=True):
            rel_name = data.get("relationship_type")
            if rel_name:
                deg_key = f"{rel_name}_degree"
                if deg_key in metrics[u]:
                    metrics[u][deg_key] += 1
                if deg_key in metrics[v]:
                    metrics[v][deg_key] += 1

        self.node_metrics = metrics
        logger.info(f"Node-level SNA metrics successfully computed for {len(metrics)} nodes.")
        return metrics

    def calculate_relation_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyzes graph structure separately for each of the 7 relationship types:
        followers, friends, mentions, replies, quotes, urls, hashtags.
        Calculates: edges, active nodes, density, average degree, connected components, largest component size.
        """
        logger.info("Computing relationship-type graph statistics...")
        relation_stats = {}

        for rel_id, rel_name in RELATIONSHIP_TYPES.items():
            subG = self.loader.get_relation_subgraph(rel_id)
            num_edges = subG.number_of_edges()
            active_nodes = [n for n, deg in subG.degree() if deg > 0]
            num_active = len(active_nodes)

            total_nodes = self.loader.num_nodes
            density = num_edges / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0.0
            avg_deg = (2.0 * num_edges / num_active) if num_active > 0 else 0.0

            # Weakly connected components on active subgraph
            if num_active > 0:
                active_subG = subG.subgraph(active_nodes)
                wcc = list(nx.weakly_connected_components(active_subG))
                num_wcc = len(wcc)
                largest_wcc = max((len(c) for c in wcc), default=0)
            else:
                num_wcc = 0
                largest_wcc = 0

            relation_stats[rel_name] = {
                "relationship_id": rel_id,
                "relationship_name": rel_name,
                "number_of_edges": num_edges,
                "number_of_active_nodes": num_active,
                "density": float(density),
                "average_degree": float(avg_deg),
                "number_of_connected_components": num_wcc,
                "largest_component_size": largest_wcc,
            }

        self.relation_stats = relation_stats
        logger.info("Relationship-type statistics successfully calculated.")
        return relation_stats

    def to_dataframe(self) -> pd.DataFrame:
        """Converts node metrics to pandas DataFrame for feature export."""
        if not self.node_metrics:
            self.calculate_node_metrics()

        rows = []
        for user_id, metrics in self.node_metrics.items():
            row = {"user_id": user_id}
            row.update(metrics)
            rows.append(row)

        df = pd.DataFrame(rows).sort_values("user_id").reset_index(drop=True)
        return df
