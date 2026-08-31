import os
import logging
from typing import Dict, Any, Optional, List, Union
import torch
import networkx as nx
from backend.config import DATASET_PATH, RELATIONSHIP_TYPES, RELATIONSHIP_NAME_TO_ID

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MGTABGraphLoader:
    """
    Graph Builder for the MGTAB multi-relational Twitter benchmark dataset.
    Loads PyTorch tensors and constructs NetworkX MultiDiGraph / DiGraph objects.
    """

    def __init__(self, data_dir: str = DATASET_PATH):
        self.data_dir = data_dir
        self.edge_index: Optional[torch.Tensor] = None
        self.edge_type: Optional[torch.Tensor] = None
        self.edge_weight: Optional[torch.Tensor] = None
        self.features: Optional[torch.Tensor] = None
        self.labels_bot: Optional[torch.Tensor] = None
        self.labels_stance: Optional[torch.Tensor] = None
        
        self.num_nodes: int = 0
        self.num_edges: int = 0
        self.graph: Optional[nx.MultiDiGraph] = None

    def load_graph_data(self) -> "MGTABGraphLoader":
        """Loads dataset tensors from disk."""
        logger.info(f"Loading MGTAB graph tensors from '{self.data_dir}'...")

        files = {
            "edge_index": "edge_index.pt",
            "edge_type": "edge_type.pt",
            "edge_weight": "edge_weight.pt",
            "features": "features.pt",
            "labels_bot": "labels_bot.pt",
            "labels_stance": "labels_stance.pt",
        }

        loaded = {}
        for name, filename in files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Required dataset tensor missing: '{filepath}'")
            loaded[name] = torch.load(filepath, map_location="cpu", weights_only=False)

        self.edge_index = loaded["edge_index"]
        self.edge_type = loaded["edge_type"]
        self.edge_weight = loaded["edge_weight"]
        self.features = loaded["features"]
        self.labels_bot = loaded["labels_bot"]
        self.labels_stance = loaded["labels_stance"]

        self.validate_graph_data()
        return self

    def validate_graph_data(self) -> bool:
        """Validates tensor shapes and alignment."""
        if self.edge_index.dim() != 2 or self.edge_index.shape[0] != 2:
            raise ValueError(f"edge_index must have shape [2, E], got {list(self.edge_index.shape)}")

        self.num_edges = self.edge_index.shape[1]
        
        if self.edge_type.shape[0] != self.num_edges:
            raise ValueError(f"edge_type length ({self.edge_type.shape[0]}) does not match edge_index count ({self.num_edges})")

        if self.edge_weight.shape[0] != self.num_edges:
            raise ValueError(f"edge_weight length ({self.edge_weight.shape[0]}) does not match edge_index count ({self.num_edges})")

        if self.features is not None:
            self.num_nodes = self.features.shape[0]
        else:
            self.num_nodes = int(self.edge_index.max().item() + 1)

        logger.info(f"Validated graph tensors: {self.num_nodes} nodes, {self.num_edges} edges.")
        return True

    def build_multidigraph(self, max_nodes: Optional[int] = None) -> nx.MultiDiGraph:
        """Constructs NetworkX MultiDiGraph preserving multi-relational directed edges."""
        if self.graph is not None and max_nodes is None:
            return self.graph

        logger.info("Constructing NetworkX MultiDiGraph from tensors...")
        G = nx.MultiDiGraph()

        # Add all node IDs with initial attributes
        nodes_to_add = range(self.num_nodes) if max_nodes is None else range(min(self.num_nodes, max_nodes))
        
        for u in nodes_to_add:
            bot_label = int(self.labels_bot[u].item()) if self.labels_bot is not None and u < len(self.labels_bot) else None
            stance_label = int(self.labels_stance[u].item()) if self.labels_stance is not None and u < len(self.labels_stance) else None
            G.add_node(u, bot_label=bot_label, stance_label=stance_label)

        # Add edges
        sources = self.edge_index[0].tolist()
        targets = self.edge_index[1].tolist()
        rel_ids = self.edge_type.tolist()
        weights = self.edge_weight.tolist()

        valid_nodes_set = set(G.nodes())

        for src, tgt, rel_id, w in zip(sources, targets, rel_ids, weights):
            if src in valid_nodes_set and tgt in valid_nodes_set:
                rel_name = RELATIONSHIP_TYPES.get(rel_id, f"relation_{rel_id}")
                G.add_edge(
                    src,
                    tgt,
                    relationship_type=rel_name,
                    relationship_id=int(rel_id),
                    weight=float(w)
                )

        logger.info(f"MultiDiGraph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        if max_nodes is None:
            self.graph = G
        return G

    def get_relation_subgraph(self, relation: Union[int, str], G: Optional[nx.MultiDiGraph] = None) -> nx.DiGraph:
        """Extracts a simple directed graph containing only edges of a specific relationship type."""
        base_g = G if G is not None else (self.graph if self.graph is not None else self.build_multidigraph())
        
        if isinstance(relation, str):
            rel_id = RELATIONSHIP_NAME_TO_ID.get(relation.lower())
            rel_name = relation.lower()
        else:
            rel_id = relation
            rel_name = RELATIONSHIP_TYPES.get(rel_id, f"relation_{rel_id}")

        subG = nx.DiGraph()
        subG.add_nodes_from(base_g.nodes(data=True))

        for u, v, k, data in base_g.edges(keys=True, data=True):
            if data.get("relationship_id") == rel_id or data.get("relationship_type") == rel_name:
                if subG.has_edge(u, v):
                    subG[u][v]["weight"] += data.get("weight", 1.0)
                else:
                    subG.add_edge(u, v, weight=data.get("weight", 1.0), relationship_type=rel_name, relationship_id=rel_id)

        return subG

    def get_user_subgraph(
        self,
        user_id: int,
        depth: int = 1,
        max_nodes: int = 100,
        relationship_type: Optional[str] = None
    ) -> nx.MultiDiGraph:
        """Extracts an ego-subgraph centered around user_id up to depth hops."""
        G = self.graph if self.graph is not None else self.build_multidigraph()
        
        if user_id not in G:
            raise KeyError(f"User ID {user_id} not found in graph.")

        if relationship_type:
            rel_id = RELATIONSHIP_NAME_TO_ID.get(relationship_type.lower())
            filtered_edges = [
                (u, v, k, d) for u, v, k, d in G.edges(keys=True, data=True)
                if d.get("relationship_type") == relationship_type.lower() or d.get("relationship_id") == rel_id
            ]
            temp_G = nx.MultiDiGraph()
            temp_G.add_nodes_from(G.nodes(data=True))
            for u, v, k, d in filtered_edges:
                temp_G.add_edge(u, v, key=k, **d)
            target_G = temp_G
        else:
            target_G = G

        # Breadth-first search for nodes within depth radius
        visited_nodes = {user_id}
        current_layer = {user_id}

        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                # Add successors and predecessors (undirected neighbourhood expansion for visualization)
                neighbors = set(target_G.successors(node)).union(set(target_G.predecessors(node)))
                for nbr in neighbors:
                    if nbr not in visited_nodes:
                        next_layer.add(nbr)
                        visited_nodes.add(nbr)
                        if len(visited_nodes) >= max_nodes:
                            break
                if len(visited_nodes) >= max_nodes:
                    break
            current_layer = next_layer
            if len(visited_nodes) >= max_nodes or not current_layer:
                break

        subgraph = target_G.subgraph(visited_nodes).copy()
        return subgraph

    def get_graph_summary(self) -> Dict[str, Any]:
        """Calculates global structural summary of the graph."""
        G = self.graph if self.graph is not None else self.build_multidigraph()
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()

        # Count edges per relationship type
        relation_counts: Dict[str, int] = {}
        for _, _, data in G.edges(data=True):
            rel_name = data.get("relationship_type", "unknown")
            relation_counts[rel_name] = relation_counts.get(rel_name, 0) + 1

        density = num_edges / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0.0

        return {
            "nodes": num_nodes,
            "edges": num_edges,
            "graph_type": "directed_multigraph",
            "density": float(density),
            "relationship_types": relation_counts,
        }
