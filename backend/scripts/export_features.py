import os
import json
import logging
import pandas as pd
from backend.config import RESULTS_PATH, DATASET_PATH
from backend.graph_builder import MGTABGraphLoader
from backend.sna import SNAAnalyzer
from backend.community import CommunityDetector
from backend.coordination import CoordinationAnalyzer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def export_sna_artifacts(
    data_dir: str = DATASET_PATH,
    results_dir: str = RESULTS_PATH
) -> None:
    """
    Runs full SNA, Community Detection, and Coordination Analysis pipeline.
    Exports results/sna_features.csv, results/communities.json, and results/sna_metadata.json.
    """
    os.makedirs(results_dir, exist_ok=True)
    logger.info(f"Starting SNA export pipeline from dataset '{data_dir}' to '{results_dir}'...")

    # 1. Load Graph
    loader = MGTABGraphLoader(data_dir=data_dir).load_graph_data()
    
    # 2. Compute SNA Metrics
    sna_analyzer = SNAAnalyzer(loader)
    node_metrics = sna_analyzer.calculate_node_metrics()
    rel_stats = sna_analyzer.calculate_relation_statistics()
    df_sna = sna_analyzer.to_dataframe()

    # 3. Detect Communities
    community_detector = CommunityDetector(loader)
    node_comm_map = community_detector.detect_communities()
    comm_stats = community_detector.calculate_community_statistics(
        pagerank_dict={n: metrics["pagerank"] for n, metrics in node_metrics.items()}
    )

    # 4. Compute Coordination Scores
    coordination_analyzer = CoordinationAnalyzer(loader)
    coordination_scores = {}
    for u in range(loader.num_nodes):
        coord_res = coordination_analyzer.calculate_user_coordination(u)
        coordination_scores[u] = coord_res

    # Merge Community and Coordination data into Feature DataFrame for ML Member
    df_sna["community_id"] = df_sna["user_id"].map(node_comm_map).fillna(-1).astype(int)
    
    comm_size_map = {c_id: data["size"] for c_id, data in comm_stats.items()}
    df_sna["community_size"] = df_sna["community_id"].map(comm_size_map).fillna(1).astype(int)
    
    df_sna["coordination_score"] = df_sna["user_id"].map(lambda u: coordination_scores[int(u)]["coordination_score"])

    # Save results/sna_features.csv
    features_csv_path = os.path.join(results_dir, "sna_features.csv")
    df_sna.to_csv(features_csv_path, index=False)
    logger.info(f"[OK] Saved SNA features CSV to '{features_csv_path}' (Shape: {df_sna.shape}).")

    # Save results/communities.json
    comm_json_path = os.path.join(results_dir, "communities.json")
    with open(comm_json_path, "w") as f:
        json.dump(comm_stats, f, indent=2)
    logger.info(f"[OK] Saved community statistics JSON to '{comm_json_path}'.")

    # Save results/sna_metadata.json
    metadata = {
        "total_nodes": loader.num_nodes,
        "total_edges": loader.num_edges,
        "graph_type": "directed_multigraph",
        "community_algorithm": community_detector.config.get("method", "louvain"),
        "total_communities": len(comm_stats),
        "relationship_types": rel_stats,
        "metrics_computed": [
            "degree", "in_degree", "out_degree", "weighted_degree",
            "degree_centrality", "pagerank", "betweenness",
            "clustering_coefficient", "community_id", "community_size",
            "coordination_score", "followers_degree", "friends_degree",
            "mentions_degree", "replies_degree", "quotes_degree",
            "urls_degree", "hashtags_degree"
        ]
    }
    metadata_json_path = os.path.join(results_dir, "sna_metadata.json")
    with open(metadata_json_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"[OK] Saved SNA metadata JSON to '{metadata_json_path}'.")

if __name__ == "__main__":
    export_sna_artifacts()
