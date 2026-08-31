import logging
from typing import Dict, Any, List, Set, Optional
import numpy as np
import networkx as nx
from backend.config import COORDINATION_WEIGHTS, RELATIONSHIP_TYPES, RELATIONSHIP_NAME_TO_ID
from backend.graph_builder import MGTABGraphLoader

logger = logging.getLogger(__name__)

class CoordinationAnalyzer:
    """
    Coordination Analysis Engine for MGTAB multi-relational graphs.
    Computes 6 interpretable network interaction signals and a heuristic coordination score.

    IMPORTANT NOTE:
    Coordination signals represent POTENTIALLY COORDINATED BEHAVIOUR based on network structure,
    NOT definitive malicious activity or proven misinformation operations.
    """

    def __init__(self, loader: MGTABGraphLoader, weights: Optional[Dict[str, float]] = None):
        self.loader = loader
        self.weights = weights or COORDINATION_WEIGHTS
        self.multigraph: nx.MultiDiGraph = self.loader.build_multidigraph()

    def calculate_interaction_density(self, user_id: int) -> float:
        """
        Signal 1 — Interaction Density:
        Measures total interaction weight and reciprocal interactions relative to degree.
        """
        G = self.multigraph
        if user_id not in G:
            return 0.0

        out_edges = list(G.out_edges(user_id, data=True))
        in_edges = list(G.in_edges(user_id, data=True))
        
        if not out_edges and not in_edges:
            return 0.0

        out_neighbors = {v for _, v, _ in out_edges}
        in_neighbors = {u for u, _, _ in in_edges}

        # Reciprocal neighbours
        reciprocal = out_neighbors.intersection(in_neighbors)
        tot_unique = out_neighbors.union(in_neighbors)

        reciprocity_ratio = len(reciprocal) / len(tot_unique) if tot_unique else 0.0
        
        # Interaction volume intensity (capped at 1.0)
        tot_weight = sum(d.get("weight", 1.0) for _, _, d in out_edges) + sum(d.get("weight", 1.0) for _, _, d in in_edges)
        volume_intensity = min(tot_weight / 50.0, 1.0)

        density_score = 0.6 * reciprocity_ratio + 0.4 * volume_intensity
        return float(np.clip(density_score, 0.0, 1.0))

    def calculate_neighbour_similarity(self, user_id: int, top_k_neighbors: int = 20) -> float:
        """
        Signal 2 — Neighbour Jaccard Similarity:
        Calculates average Jaccard similarity of neighbourhood with user's top connected neighbours.
        """
        G = self.multigraph
        if user_id not in G:
            return 0.0

        user_neighbors = set(G.successors(user_id)).union(set(G.predecessors(user_id)))
        if not user_neighbors:
            return 0.0

        similarities = []
        for nbr in list(user_neighbors)[:top_k_neighbors]:
            nbr_neighbors = set(G.successors(nbr)).union(set(G.predecessors(nbr)))
            if nbr_neighbors:
                intersection = user_neighbors.intersection(nbr_neighbors)
                union = user_neighbors.union(nbr_neighbors)
                jaccard = len(intersection) / len(union) if union else 0.0
                similarities.append(jaccard)

        avg_jaccard = np.mean(similarities) if similarities else 0.0
        return float(np.clip(avg_jaccard, 0.0, 1.0))

    def calculate_shared_content_similarity(self, user_id: int, relation_name: str) -> float:
        """
        Signal 3 & 4 — Shared URLs / Shared Hashtags:
        Measures overlap with neighbours on relation graphs (URLs: type 5, Hashtags: type 6).
        """
        G = self.multigraph
        if user_id not in G:
            return 0.0

        rel_id = RELATIONSHIP_NAME_TO_ID.get(relation_name.lower())
        
        # Extract items connected to user_id for this relation type
        user_items = {
            v for _, v, d in G.out_edges(user_id, data=True)
            if d.get("relationship_type") == relation_name.lower() or d.get("relationship_id") == rel_id
        }

        if not user_items:
            return 0.0

        # Check overlapping items among successors
        successors = list(G.successors(user_id))
        overlaps = []

        for succ in successors[:15]:
            succ_items = {
                v for _, v, d in G.out_edges(succ, data=True)
                if d.get("relationship_type") == relation_name.lower() or d.get("relationship_id") == rel_id
            }
            if succ_items:
                jaccard = len(user_items.intersection(succ_items)) / len(user_items.union(succ_items))
                overlaps.append(jaccard)

        avg_overlap = np.mean(overlaps) if overlaps else 0.0
        return float(np.clip(avg_overlap, 0.0, 1.0))

    def calculate_relationship_pattern_vector(self, user_id: int) -> np.ndarray:
        """
        Constructs normalized 7-dimensional vector representing interaction counts
        across relationship types (followers, friends, mentions, replies, quotes, urls, hashtags).
        """
        G = self.multigraph
        vec = np.zeros(len(RELATIONSHIP_TYPES), dtype=np.float32)

        if user_id not in G:
            return vec

        for _, _, d in G.out_edges(user_id, data=True):
            rel_id = d.get("relationship_id", 0)
            if 0 <= rel_id < len(RELATIONSHIP_TYPES):
                vec[rel_id] += float(d.get("weight", 1.0))

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def calculate_relationship_similarity(self, user_id: int) -> float:
        """
        Signal 6 — Relationship Pattern Cosine Similarity:
        Calculates average cosine similarity of user's relationship vector with direct neighbours.
        """
        G = self.multigraph
        if user_id not in G:
            return 0.0

        user_vec = self.calculate_relationship_pattern_vector(user_id)
        if np.all(user_vec == 0):
            return 0.0

        neighbors = set(G.successors(user_id)).union(set(G.predecessors(user_id)))
        if not neighbors:
            return 0.0

        sims = []
        for nbr in list(neighbors)[:15]:
            nbr_vec = self.calculate_relationship_pattern_vector(nbr)
            if not np.all(nbr_vec == 0):
                cos_sim = float(np.dot(user_vec, nbr_vec))
                sims.append(cos_sim)

        avg_cos = np.mean(sims) if sims else 0.0
        return float(np.clip(avg_cos, 0.0, 1.0))

    def calculate_user_coordination(self, user_id: int) -> Dict[str, Any]:
        """
        Calculates overall coordination score and signal breakdown for a single user.
        Returns cautious, interpretable risk levels.
        """
        density_signal = self.calculate_interaction_density(user_id)
        neighbour_signal = self.calculate_neighbour_similarity(user_id)
        url_signal = self.calculate_shared_content_similarity(user_id, "urls")
        hashtag_signal = self.calculate_shared_content_similarity(user_id, "hashtags")
        rel_pattern_signal = self.calculate_relationship_similarity(user_id)

        shared_content_signal = max(url_signal, hashtag_signal)

        # Weighted heuristic combination
        w_dens = self.weights.get("w_interaction_density", 0.30)
        w_nbr = self.weights.get("w_neighbour_similarity", 0.25)
        w_cnt = self.weights.get("w_shared_content", 0.25)
        w_rel = self.weights.get("w_relationship_similarity", 0.20)

        score = (
            w_dens * density_signal +
            w_nbr * neighbour_signal +
            w_cnt * shared_content_signal +
            w_rel * rel_pattern_signal
        )
        score = float(np.clip(score, 0.0, 1.0))

        # Determine risk level using cautious terminology
        if score >= 0.70:
            risk_level = "high"
            interpretation = "Potentially coordinated behavioural pattern detected based on network interaction signals."
        elif score >= 0.40:
            risk_level = "moderate"
            interpretation = "Moderate structural interaction similarity observed among surrounding network neighbourhood."
        else:
            risk_level = "low"
            interpretation = "Normal, uncoordinated network interaction patterns."

        return {
            "coordination_score": round(score, 4),
            "risk_level": risk_level,
            "signals": {
                "interaction_density": round(density_signal, 4),
                "neighbour_similarity": round(neighbour_signal, 4),
                "shared_url_similarity": round(url_signal, 4),
                "shared_hashtag_similarity": round(hashtag_signal, 4),
                "relationship_similarity": round(rel_pattern_signal, 4),
            },
            "interpretation": interpretation
        }

    def analyze_community_coordination(self, community_nodes: List[int]) -> Dict[str, Any]:
        """
        Analyzes coordination signals aggregated across a community node set.
        """
        if not community_nodes:
            return {"avg_coordination_score": 0.0, "risk_level": "low", "suspicious_node_count": 0}

        scores = []
        high_risk_count = 0

        for u in community_nodes:
            res = self.calculate_user_coordination(u)
            scores.append(res["coordination_score"])
            if res["risk_level"] == "high":
                high_risk_count += 1

        avg_score = float(np.mean(scores)) if scores else 0.0

        if avg_score >= 0.65 or (high_risk_count / len(community_nodes) >= 0.3):
            comm_risk = "high"
            interpretation = "Suspiciously dense community with high internal interaction concentration."
        elif avg_score >= 0.35:
            comm_risk = "moderate"
            interpretation = "Moderate interaction similarity detected within community."
        else:
            comm_risk = "low"
            interpretation = "Standard community structure without prominent coordination signals."

        return {
            "avg_coordination_score": round(avg_score, 4),
            "risk_level": comm_risk,
            "suspicious_node_count": high_risk_count,
            "interpretation": interpretation
        }
