import os
from typing import Dict, Any

# Dataset and Output Paths
DATASET_PATH: str = os.getenv("DATASET_PATH", "dataset")
RESULTS_PATH: str = os.getenv("RESULTS_PATH", "results")
MODELS_PATH: str = os.getenv("MODELS_PATH", "models")

# MGTAB Standard Multi-Relational Edge Type Mapping
RELATIONSHIP_TYPES: Dict[int, str] = {
    0: "followers",
    1: "friends",
    2: "mentions",
    3: "replies",
    4: "quotes",
    5: "urls",
    6: "hashtags"
}

RELATIONSHIP_NAME_TO_ID: Dict[str, int] = {v: k for k, v in RELATIONSHIP_TYPES.items()}

# SNA & Graph Processing Configuration
SNA_CONFIG: Dict[str, Any] = {
    "compute_betweenness": False,
    "betweenness_k": 100,
    "compute_clustering": True,
    "pagerank_alpha": 0.85,
    "pagerank_max_iter": 100,
    "max_network_nodes": 10000,
}

# Community Detection Configuration
COMMUNITY_CONFIG: Dict[str, Any] = {
    "method": "louvain",  # 'louvain', 'leiden', or 'components'
    "resolution": 1.0,
    "random_state": 42
}

# Coordination Analysis Weights
COORDINATION_WEIGHTS: Dict[str, float] = {
    "w_interaction_density": 0.30,
    "w_neighbour_similarity": 0.25,
    "w_shared_content": 0.25,
    "w_relationship_similarity": 0.20
}

# Cache Settings
CACHE_ENABLED: bool = True
