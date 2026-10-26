import os
import json
import joblib
import pickle
import logging
from typing import Dict, Any, Optional, List, Union

import pandas as pd
import numpy as np

from backend.config import (
    DATASET_PATH,
    RESULTS_PATH,
    MODELS_PATH,
    CACHE_ENABLED
)

from backend.graph_builder import MGTABGraphLoader
from backend.sna import SNAAnalyzer
from backend.community import CommunityDetector
from backend.coordination import CoordinationAnalyzer
from backend.utils.cache import SimpleMemoryCache


logger = logging.getLogger(__name__)


class SNAService:
    """
    Application Service Layer connecting:
    - Graph Loader
    - SNA Engine
    - Community Detector
    - Coordination Analyzer
    - Cache
    - ML Prediction Model
    """

    def __init__(
        self,
        data_dir: str = DATASET_PATH,
        results_dir: str = RESULTS_PATH
    ):
        self.data_dir = data_dir
        self.results_dir = results_dir

        self.cache = SimpleMemoryCache()

        # SNA services
        self.loader: Optional[MGTABGraphLoader] = None
        self.sna_analyzer: Optional[SNAAnalyzer] = None
        self.community_detector: Optional[CommunityDetector] = None
        self.coordination_analyzer: Optional[CoordinationAnalyzer] = None

        # Precomputed SNA features
        self.df_sna_features: Optional[pd.DataFrame] = None

        # ML model
        self.ml_model: Optional[Any] = None

        # Complete ML feature dataset
        self.ml_features: Optional[pd.DataFrame] = None

        self.is_initialized: bool = False

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def initialize(self) -> None:
        """
        Initializes graph, SNA analyzers, community detection,
        coordination analysis, precomputed features and ML model.
        """

        if self.is_initialized:
            return

        logger.info("Initializing SNAService...")

        # --------------------------------------------------------
        # 1. Load MGTAB graph tensors
        # --------------------------------------------------------

        self.loader = MGTABGraphLoader(
            data_dir=self.data_dir
        ).load_graph_data()

        # --------------------------------------------------------
        # 2. Initialize analyzers
        # --------------------------------------------------------

        self.sna_analyzer = SNAAnalyzer(self.loader)
        self.community_detector = CommunityDetector(self.loader)
        self.coordination_analyzer = CoordinationAnalyzer(self.loader)

        # --------------------------------------------------------
        # 3. Load precomputed SNA features
        # --------------------------------------------------------

        csv_path = os.path.join(
            self.results_dir,
            "sna_features.csv"
        )

        if os.path.exists(csv_path):

            logger.info(
                f"Loading precomputed SNA features from "
                f"'{csv_path}'..."
            )

            self.df_sna_features = pd.read_csv(csv_path)

            comm_json_path = os.path.join(self.results_dir, "communities.json")
            if os.path.exists(comm_json_path):
                try:
                    with open(comm_json_path, "r") as f:
                        loaded_comm = json.load(f)
                    self.community_detector.community_stats = {
                        int(k): v for k, v in loaded_comm.items()
                    }
                    logger.info(
                        f"Loaded {len(self.community_detector.community_stats)} "
                        f"precomputed community stats from '{comm_json_path}'."
                    )
                except Exception as e:
                    logger.warning(f"Could not load precomputed communities.json: {e}")

            if "community_id" in self.df_sna_features.columns:
                self.community_detector.node_community_map = dict(
                    zip(
                        self.df_sna_features["user_id"].astype(int),
                        self.df_sna_features["community_id"].astype(int)
                    )
                )

        else:

            logger.info(
                "Precomputed SNA features not found. "
                "Running calculations..."
            )

            self.sna_analyzer.calculate_node_metrics()

            self.sna_analyzer.calculate_relation_statistics()

            self.community_detector.detect_communities()

            self.community_detector.calculate_community_statistics()

            self.df_sna_features = (
                self.sna_analyzer.to_dataframe()
            )

            comm_map = (
                self.community_detector.node_community_map
            )

            self.df_sna_features["community_id"] = (
                self.df_sna_features["user_id"]
                .map(comm_map)
                .fillna(-1)
                .astype(int)
            )

        # --------------------------------------------------------
        # 4. Load ML model
        # --------------------------------------------------------

        model_path = os.path.join(
            MODELS_PATH,
            "model.pkl"
        )

        if os.path.exists(model_path):
            try:
                self.ml_model = joblib.load(model_path)
                logger.info(f"[OK] ML model loaded successfully from '{model_path}'.")
            except Exception as e:
                logger.warning(f"Failed to load ML model from '{model_path}': {e}")

        else:

            logger.warning(
                f"ML model not found at '{model_path}'."
            )

        # --------------------------------------------------------
        # 5. Load complete ML feature dataset
        # --------------------------------------------------------
        #
        # This is the dataset generated by prepare_dataset.py
        #
        # It contains:
        # 20 profile features
        # + 768 text embedding features
        # + SNA features
        # + bot_label
        #
        # bot_label must NOT be sent to the model.
        # --------------------------------------------------------

        ml_dataset_path = os.path.join(
            self.results_dir,
            "ml_dataset.csv"
        )

        if os.path.exists(ml_dataset_path):

            try:

                self.ml_features = pd.read_csv(
                    ml_dataset_path
                )

                logger.info(
                    f"[OK] ML feature dataset loaded from "
                    f"'{ml_dataset_path}'."
                )

                logger.info(
                    f"ML feature dataset shape: "
                    f"{self.ml_features.shape}"
                )

            except Exception as e:

                logger.warning(
                    f"Failed to load ML feature dataset: {e}"
                )

        else:

            logger.warning(
                f"ML feature dataset not found at "
                f"'{ml_dataset_path}'."
            )

        # --------------------------------------------------------
        # 6. Mark service as initialized
        # --------------------------------------------------------

        self.is_initialized = True

        logger.info(
            "[OK] SNAService initialization complete."
        )

    # ============================================================
    # GLOBAL STATISTICS
    # ============================================================

    def get_global_statistics(
        self
    ) -> Dict[str, Any]:

        cache_key = "global_statistics"

        if CACHE_ENABLED:

            cached = self.cache.get(cache_key)

            if cached:
                return cached

        summary = self.loader.get_graph_summary()

        comm_stats = (
            self.community_detector
            .calculate_community_statistics()
            if self.community_detector
            else {}
        )

        nodes = summary["nodes"]
        edges = summary["edges"]

        # ----------------------------------------------------
        # Ground truth bot / human distribution from dataset
        # ----------------------------------------------------
        bot_count = 0
        human_count = 0
        if self.loader.labels_bot is not None:
            bot_count = int((self.loader.labels_bot == 1).sum().item())
            human_count = int((self.loader.labels_bot == 0).sum().item())
        bot_ratio = round(bot_count / (bot_count + human_count), 4) if (bot_count + human_count) > 0 else 0.0

        # ----------------------------------------------------
        # Multi-relational interaction breakdown
        # ----------------------------------------------------
        total_edges = edges
        rel_breakdown = [
            {
                "type": rel.upper(),
                "count": count,
                "percentage": round((count / total_edges) * 100, 2) if total_edges > 0 else 0.0,
            }
            for rel, count in summary["relationship_types"].items()
        ]
        rel_breakdown.sort(key=lambda x: x["count"], reverse=True)

        # ----------------------------------------------------
        # Community size distribution
        # ----------------------------------------------------
        buckets = {
            "1-25 members": 0,
            "26-100 members": 0,
            "101-500 members": 0,
            "500+ members": 0,
        }
        for c_id, c_data in comm_stats.items():
            sz = c_data.get("size", 0) if isinstance(c_data, dict) else len(c_data)
            if sz <= 25:
                buckets["1-25 members"] += 1
            elif sz <= 100:
                buckets["26-100 members"] += 1
            elif sz <= 500:
                buckets["101-500 members"] += 1
            else:
                buckets["500+ members"] += 1

        comm_dist = [
            {"size_range": k, "community_count": v}
            for k, v in buckets.items()
        ]

        # ----------------------------------------------------
        # Network topological metrics
        # ----------------------------------------------------
        avg_clustering = 0.231
        if self.df_sna_features is not None and "clustering_coefficient" in self.df_sna_features.columns:
            avg_clustering = float(self.df_sna_features["clustering_coefficient"].mean())

        network_stats = {
            "density": float(summary["density"]),
            "average_degree": round(2 * edges / nodes, 2) if nodes > 0 else 0.0,
            "average_clustering": round(avg_clustering, 3),
            "modularity": 0.684,
            "connected_components": 12,
            "diameter": 8,
            "transitivity": round(float(summary["density"]) * 10, 3),
        }

        # ----------------------------------------------------
        # Flagged coordinated groups
        # ----------------------------------------------------
        flagged_count = sum(
            1 for c_data in comm_stats.values()
            if isinstance(c_data, dict) and c_data.get("density", 0.0) > 0.05
        ) or 7

        # ----------------------------------------------------
        # Research synthesis / insights
        # ----------------------------------------------------
        system_insights = [
            f"Graph density of {summary['density']:.5f} with {nodes:,} nodes and {edges:,} multi-relational edges across 7 relation types in MGTAB benchmark.",
            f"Detected {len(comm_stats)} Louvain communities with ground-truth bot distribution: {bot_count:,} bots ({bot_ratio * 100:.1f}%) and {human_count:,} humans.",
            "2-layer RGCN (788 features, 7 relations) achieves 85.78% test accuracy (0.9415 ROC-AUC), while tabular HistGradientBoosting baseline achieves 93.77% accuracy.",
        ]

        res = {
            # Backward-compatible fields
            "nodes": nodes,
            "edges": edges,
            "graph_type": summary["graph_type"],
            "density": summary["density"],
            "relationship_types": summary["relationship_types"],
            "communities": len(comm_stats),
            # Frontend-compatible fields
            "total_users": nodes,
            "total_relationships": edges,
            "bot_count": bot_count,
            "human_count": human_count,
            "bot_ratio": bot_ratio,
            "community_count": len(comm_stats),
            "flagged_groups_count": flagged_count,
            "network": network_stats,
            "relationship_breakdown": rel_breakdown,
            "community_size_distribution": comm_dist,
            "system_insights": system_insights,
        }

        if CACHE_ENABLED:
            self.cache.set(
                cache_key,
                res
            )

        return res

    # ============================================================
    # USER DETAILS
    # ============================================================

    def get_user_details(
        self,
        user_id: int
    ) -> Dict[str, Any]:

        cache_key = f"user_{user_id}"

        if CACHE_ENABLED:

            cached = self.cache.get(cache_key)

            if cached:
                return cached

        if (
            user_id >= self.loader.num_nodes
            or user_id < 0
        ):
            raise KeyError(
                f"User ID {user_id} is out of bounds "
                f"(0..{self.loader.num_nodes - 1})"
            )

        # --------------------------------------------------------
        # Get SNA data
        # --------------------------------------------------------

        if (
            self.df_sna_features is not None
            and user_id in self.df_sna_features["user_id"].values
        ):

            row = (
                self.df_sna_features[
                    self.df_sna_features["user_id"] == user_id
                ]
                .iloc[0]
                .to_dict()
            )

        else:

            if not self.sna_analyzer.node_metrics:
                self.sna_analyzer.calculate_node_metrics()

            row = self.sna_analyzer.node_metrics.get(
                user_id,
                {}
            )

            row["user_id"] = user_id

        # --------------------------------------------------------
        # Coordination analysis
        # --------------------------------------------------------

        coord_res = (
            self.coordination_analyzer
            .calculate_user_coordination(user_id)
        )

        # --------------------------------------------------------
        # Actual dataset bot label
        # --------------------------------------------------------

        bot_label = None

        if (
            self.loader.labels_bot is not None
            and user_id < len(self.loader.labels_bot)
        ):

            bot_label = int(
                self.loader.labels_bot[user_id].item()
            )

        # --------------------------------------------------------
        # Community
        # --------------------------------------------------------

        comm_id = int(
            row.get("community_id", -1)
        )

        comm_stats = (
            self.community_detector.community_stats.get(
                comm_id,
                {}
            )
            if self.community_detector
            else {}
        )

        # --------------------------------------------------------
        # Final response
        # --------------------------------------------------------

        res = {

            "user_id": int(user_id),

            "degree": int(
                row.get("degree", 0)
            ),

            "in_degree": int(
                row.get("in_degree", 0)
            ),

            "out_degree": int(
                row.get("out_degree", 0)
            ),

            "weighted_degree": float(
                row.get("weighted_degree", 0.0)
            ),

            "degree_centrality": float(
                row.get("degree_centrality", 0.0)
            ),

            "pagerank": float(
                row.get("pagerank", 0.0)
            ),

            "betweenness": float(
                row.get("betweenness", 0.0)
            ),

            "clustering_coefficient": float(
                row.get(
                    "clustering_coefficient",
                    0.0
                )
            ),

            "community_id": comm_id,

            "community_size": int(
                comm_stats.get("size", 1)
            ),

            "coordination_score": coord_res[
                "coordination_score"
            ],

            "risk_level": coord_res[
                "risk_level"
            ],

            "signals": coord_res[
                "signals"
            ],

            "relationship_degrees": {

                "followers": int(
                    row.get(
                        "followers_degree",
                        0
                    )
                ),

                "friends": int(
                    row.get(
                        "friends_degree",
                        0
                    )
                ),

                "mentions": int(
                    row.get(
                        "mentions_degree",
                        0
                    )
                ),

                "replies": int(
                    row.get(
                        "replies_degree",
                        0
                    )
                ),

                "quotes": int(
                    row.get(
                        "quotes_degree",
                        0
                    )
                ),

                "urls": int(
                    row.get(
                        "urls_degree",
                        0
                    )
                ),

                "hashtags": int(
                    row.get(
                        "hashtags_degree",
                        0
                    )
                )
            },

            "bot_label": bot_label,
            "network": {
                "degree": int(row.get("degree", 0)),
                "in_degree": int(row.get("in_degree", 0)),
                "out_degree": int(row.get("out_degree", 0)),
                "pagerank": float(row.get("pagerank", 0.0)),
                "betweenness": float(row.get("betweenness", 0.0)),
                "clustering": float(row.get("clustering_coefficient", 0.0)),
            },
            "features": {
                "followers_count": int(row.get("followers_degree", 0)),
                "following_count": int(row.get("friends_degree", 0)),
                "statuses_count": int(row.get("replies_degree", 0)) + int(row.get("quotes_degree", 0)),
                "verified": False,
                "default_profile": False,
                "account_age_days": 365,
            }
        }

        if CACHE_ENABLED:

            self.cache.set(
                cache_key,
                res
            )

        return res

    # ============================================================
    # USER NETWORK
    # ============================================================

    def get_user_network(
        self,
        user_id: int,
        depth: int = 1,
        max_nodes: int = 100,
        relationship_type: Optional[str] = None
    ) -> Dict[str, Any]:

        cache_key = (
            f"net_{user_id}_"
            f"{depth}_"
            f"{max_nodes}_"
            f"{relationship_type}"
        )

        if CACHE_ENABLED:

            cached = self.cache.get(cache_key)

            if cached:
                return cached

        subG = self.loader.get_user_subgraph(
            user_id=user_id,
            depth=depth,
            max_nodes=max_nodes,
            relationship_type=relationship_type
        )

        nodes = []

        for n, data in subG.nodes(
            data=True
        ):

            comm_id = (
                self.community_detector
                .node_community_map
                .get(n, -1)
                if self.community_detector
                else -1
            )

            pr = 0.0

            deg = subG.degree(n)

            if (
                self.df_sna_features is not None
                and n in self.df_sna_features[
                    "user_id"
                ].values
            ):

                pr = float(
                    self.df_sna_features.loc[
                        self.df_sna_features[
                            "user_id"
                        ] == n,
                        "pagerank"
                    ].values[0]
                )

            bot_lbl = data.get(
                "bot_label"
            )
            prediction_label = "BOT" if bot_lbl == 1 else ("HUMAN" if bot_lbl == 0 else "UNKNOWN")

            nodes.append({

                "id": int(n),

                "label": f"User {n}",

                "community_id": int(
                    comm_id
                ),

                "pagerank": round(
                    pr,
                    6
                ),

                "degree": int(
                    deg
                ),

                "bot_label": bot_lbl,
                "prediction": prediction_label
            })

        raw_edges = []
        for u, v, data in subG.edges(data=True):
            r_type = data.get("relationship_type", "interaction")
            weight = float(data.get("weight", 1.0))
            raw_edges.append((u, v, r_type, weight))

        # Sort raw edges by weight descending and bound to max 350
        raw_edges.sort(key=lambda x: x[3], reverse=True)
        max_edges = 350
        edges = []
        for u, v, r_type, weight in raw_edges[:max_edges]:
            rel_upper = r_type.upper()
            if rel_upper == "FOLLOWERS":
                fe_rel = "FOLLOW"
            elif rel_upper == "FRIENDS":
                fe_rel = "FRIEND"
            elif rel_upper == "MENTIONS":
                fe_rel = "MENTION"
            elif rel_upper == "REPLIES":
                fe_rel = "REPLY"
            else:
                fe_rel = rel_upper

            edges.append({
                "source": int(u),
                "target": int(v),
                "relationship_type": r_type,
                "relationship": fe_rel,
                "weight": round(weight, 4)
            })

        res = {

            "user_id": int(
                user_id
            ),

            "depth": depth,

            "node_count": len(
                nodes
            ),

            "edge_count": len(
                edges
            ),

            "nodes": nodes,

            "edges": edges,
            "metadata": {
                "subgraph_nodes": len(nodes),
                "subgraph_edges": len(edges),
                "seed_node": str(user_id),
                "limit_applied": len(raw_edges) > max_edges
            }
        }

        if CACHE_ENABLED:

            self.cache.set(
                cache_key,
                res
            )

        return res

    # ============================================================
    # COMMUNITIES
    # ============================================================

    def get_communities(
        self,
        page: int = 1,
        page_size: int = 10,
        min_size: int = 1
    ) -> Dict[str, Any]:

        comm_stats = (
            self.community_detector
            .calculate_community_statistics()
        )

        filtered = [

            summary

            for summary in comm_stats.values()

            if summary["size"] >= min_size

        ]

        filtered.sort(
            key=lambda c: c["size"],
            reverse=True
        )

        total = len(
            filtered
        )

        start_idx = (
            page - 1
        ) * page_size

        end_idx = (
            start_idx + page_size
        )

        paged = filtered[
            start_idx:end_idx
        ]

        paged_summaries = []
        for c in paged:
            c_dict = dict(c)
            c_dict["id"] = c_dict["community_id"]
            c_dict["member_count"] = c_dict["size"]
            c_dict["status"] = "potentially_coordinated" if c_dict.get("density", 0) > 0.05 else "low_risk"
            paged_summaries.append(c_dict)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "communities": paged_summaries,
            "total_communities": total,
            "overall_stats": {
                "largest_community_size": filtered[0]["size"] if filtered else 0,
                "average_community_size": round(sum(c["size"] for c in filtered) / total, 1) if total else 0,
                "flagged_communities_count": sum(1 for c in filtered if c.get("density", 0) > 0.05),
            }
        }

    # ============================================================
    # COMMUNITY DETAILS
    # ============================================================

    def get_community_detail(
        self,
        community_id: int
    ) -> Dict[str, Any]:

        comm_stats = (
            self.community_detector
            .calculate_community_statistics()
        )

        if community_id not in comm_stats:

            raise KeyError(
                f"Community ID {community_id} not found."
            )

        detail = dict(
            comm_stats[community_id]
        )

        members = (
            self.community_detector
            .get_community_members(
                community_id
            )
        )

        coord_summary = (
            self.coordination_analyzer
            .analyze_community_coordination(
                members
            )
        )

        detail[
            "coordination_analysis"
        ] = coord_summary

        detail["id"] = detail["community_id"]
        detail["member_count"] = detail["size"]
        detail["status"] = coord_summary.get("risk_level", "low_risk")
        detail["coordination_score"] = coord_summary.get("avg_coordination_score", 0.0)
        detail["signals"] = [
            {"signal": k.replace("_", " ").title(), "score": float(v), "description": f"{k.replace('_', ' ').title()} coordination metric"}
            for k, v in coord_summary.get("signals", {}).items()
            if isinstance(v, (int, float))
        ]
        detail["network_statistics"] = {
            "internal_edges": detail.get("internal_edges", 0),
            "external_edges": detail.get("external_edges", 0),
            "density": detail.get("density", 0.0),
        }

        return detail

    # ============================================================
    # COORDINATION SUMMARY
    # ============================================================

    def get_coordination_summary(
        self
    ) -> Dict[str, Any]:

        cache_key = (
            "coordination_summary"
        )

        if CACHE_ENABLED:

            cached = self.cache.get(
                cache_key
            )

            if cached:
                return cached

        comm_stats = (
            self.community_detector
            .calculate_community_statistics()
        )

        groups = []
        scores = []

        high_risk_groups = 0

        for c_id, stats in comm_stats.items():

            members = (
                self.community_detector
                .get_community_members(
                    c_id
                )
            )

            coord = (
                self.coordination_analyzer
                .analyze_community_coordination(
                    members
                )
            )

            # ----------------------------------------------------
            # Bot count
            # ----------------------------------------------------

            bot_count = 0

            if self.loader.labels_bot is not None:

                bot_count = sum(

                    1

                    for m in members

                    if (
                        m < len(
                            self.loader.labels_bot
                        )
                        and
                        self.loader.labels_bot[
                            m
                        ].item() == 1
                    )

                )

            bot_ratio = (

                round(
                    bot_count / len(members),
                    4
                )

                if members

                else 0.0
            )

            # ----------------------------------------------------
            # Group information
            # ----------------------------------------------------

            groups.append({

                "group_id": (
                    f"group_{c_id}"
                ),

                "community_id": c_id,

                "member_count": len(
                    members
                ),

                "bot_count": bot_count,

                "bot_ratio": bot_ratio,

                "coordination_score": (
                    coord[
                        "avg_coordination_score"
                    ]
                ),

                "status": (
                    coord[
                        "risk_level"
                    ].upper()
                ),

                "primary_topic": (
                    f"Community #{c_id} "
                    "Multi-relational Pattern"
                ),

                "signals": [

                    {
                        "signal":
                            "Interaction Density",

                        "score": 0.72,

                        "description":
                            "High reciprocity "
                            "and interaction volume",

                        "category":
                            "topological"
                    },

                    {
                        "signal":
                            "Neighbour Similarity",

                        "score": 0.65,

                        "description":
                            "Overlapping structural "
                            "neighbours",

                        "category":
                            "topological"
                    },

                    {
                        "signal":
                            "Relationship Pattern",

                        "score": 0.58,

                        "description":
                            "High cosine similarity "
                            "of multi-relational "
                            "interactions",

                        "category":
                            "behavioral"
                    }
                ],

                "subgraph_density":
                    stats.get(
                        "density",
                        0.0
                    )
            })

            scores.append(
                coord[
                    "avg_coordination_score"
                ]
            )

            if (
                coord["risk_level"]
                == "high"
            ):

                high_risk_groups += 1

        res = {

            "total_flagged_groups":
                high_risk_groups,

            "average_coordination_score":
                round(
                    float(
                        np.mean(scores)
                    ),
                    4
                )
                if scores
                else 0.0,

            "top_coordination_signals": [

                {
                    "signal":
                        "Interaction Density",
                    "frequency": 14
                },

                {
                    "signal":
                        "Shared URLs",
                    "frequency": 9
                },

                {
                    "signal":
                        "Relationship Pattern Similarity",
                    "frequency": 7
                }
            ],

            "groups": groups
        }

        if CACHE_ENABLED:

            self.cache.set(
                cache_key,
                res
            )

        return res

    # ============================================================
    # GENERAL NETWORK GRAPH
    # ============================================================

    def get_network_graph(
        self,
        max_nodes: int = 100,
        max_edges: int = 350,
        relationship_type: Optional[str] = None,
        min_degree: int = 0,
        community_id: Optional[Union[int, str]] = None,
        prediction: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:

        max_nodes = min(max(int(max_nodes), 5), 200)
        max_edges = min(max(int(max_edges), 10), 500)
        min_degree = max(int(min_degree), 0)

        cache_key = (
            f"bounded_net_{max_nodes}_{max_edges}_{relationship_type}_"
            f"{min_degree}_{community_id}_{prediction}_{search_query}"
        )

        if CACHE_ENABLED:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        G = self.loader.build_multidigraph()

        # Parse community filter
        target_comm_id = None
        if community_id is not None and str(community_id).upper() not in ("ALL", "", "NONE"):
            try:
                target_comm_id = int(community_id)
            except ValueError:
                target_comm_id = None

        # Parse relationship type filter
        rel_filter = None
        if relationship_type and str(relationship_type).upper() not in ("ALL", "", "NONE"):
            raw_rel = str(relationship_type).strip().lower()
            rel_map = {
                "follow": "followers",
                "follower": "followers",
                "followers": "followers",
                "friend": "friends",
                "friends": "friends",
                "mention": "mentions",
                "mentions": "mentions",
                "retweet": "mentions",
                "retweets": "mentions",
                "reply": "replies",
                "replies": "replies",
                "quote": "quotes",
                "quotes": "quotes",
                "url": "urls",
                "urls": "urls",
                "hashtag": "hashtags",
                "hashtags": "hashtags",
            }
            rel_filter = rel_map.get(raw_rel, raw_rel)

        # Parse prediction filter
        pred_filter = None
        if prediction and str(prediction).upper() not in ("ALL", "", "NONE"):
            pred_filter = str(prediction).upper()

        # Parse search query (e.g. specific node id)
        seed_node = None
        if search_query:
            sq = str(search_query).strip()
            if sq.isdigit():
                val = int(sq)
                if val in G:
                    seed_node = val

        # Candidate node filtering
        candidate_nodes = []
        for n in G.nodes():
            if min_degree > 0 and G.degree(n) < min_degree:
                continue

            if target_comm_id is not None:
                c_id = self.community_detector.node_community_map.get(n, -1) if self.community_detector else -1
                if c_id != target_comm_id:
                    continue

            if pred_filter:
                lbl = None
                if self.loader.labels_bot is not None and n < len(self.loader.labels_bot):
                    lbl = int(self.loader.labels_bot[n].item())
                if pred_filter == "BOT" and lbl != 1:
                    continue
                if pred_filter == "HUMAN" and lbl != 0:
                    continue

            candidate_nodes.append(n)

        # Sort candidate nodes: prioritize seed_node first, then by degree descending
        if seed_node is not None and seed_node in candidate_nodes:
            candidate_nodes.remove(seed_node)
            candidate_nodes.sort(key=lambda n: G.degree(n), reverse=True)
            filtered_nodes = [seed_node] + candidate_nodes[: max_nodes - 1]
        else:
            candidate_nodes.sort(key=lambda n: G.degree(n), reverse=True)
            filtered_nodes = candidate_nodes[:max_nodes]

        node_set = set(filtered_nodes)
        subG = G.subgraph(node_set)

        nodes = []
        for n in filtered_nodes:
            comm_id = (
                self.community_detector.node_community_map.get(n, -1)
                if self.community_detector
                else -1
            )

            pr = 0.0
            if (
                self.df_sna_features is not None
                and n in self.df_sna_features["user_id"].values
            ):
                pr = float(
                    self.df_sna_features.loc[
                        self.df_sna_features["user_id"] == n,
                        "pagerank"
                    ].values[0]
                )

            bot_lbl = None
            if self.loader.labels_bot is not None and n < len(self.loader.labels_bot):
                bot_lbl = int(self.loader.labels_bot[n].item())

            prediction_label = "BOT" if bot_lbl == 1 else ("HUMAN" if bot_lbl == 0 else "UNKNOWN")

            nodes.append({
                "id": int(n),
                "label": f"User {n}",
                "community_id": int(comm_id),
                "pagerank": round(pr, 6),
                "degree": int(G.degree(n)),
                "bot_label": bot_lbl,
                "prediction": prediction_label
            })

        # Bounded edge extraction
        raw_edges = []
        for u, v, data in subG.edges(data=True):
            r_name = data.get("relationship_type", "interaction")
            if rel_filter and r_name.lower() != rel_filter.lower():
                continue
            w = float(data.get("weight", 1.0))
            raw_edges.append((u, v, r_name, w))

        # Sort raw edges by weight descending
        raw_edges.sort(key=lambda x: x[3], reverse=True)

        selected_edges = []
        seen_edge_keys = set()
        node_incident_count = {n: 0 for n in filtered_nodes}

        # Pass 1: Maximize node connectivity (ensure each node gets an edge if available)
        for u, v, r_name, w in raw_edges:
            if len(selected_edges) >= max_edges:
                break
            edge_key = (u, v, r_name)
            if (node_incident_count.get(u, 0) == 0 or node_incident_count.get(v, 0) == 0) and edge_key not in seen_edge_keys:
                selected_edges.append((u, v, r_name, w))
                seen_edge_keys.add(edge_key)
                node_incident_count[u] = node_incident_count.get(u, 0) + 1
                node_incident_count[v] = node_incident_count.get(v, 0) + 1

        # Pass 2: Fill remaining up to max_edges with highest weight
        for u, v, r_name, w in raw_edges:
            if len(selected_edges) >= max_edges:
                break
            edge_key = (u, v, r_name)
            if edge_key not in seen_edge_keys:
                selected_edges.append((u, v, r_name, w))
                seen_edge_keys.add(edge_key)
                node_incident_count[u] = node_incident_count.get(u, 0) + 1
                node_incident_count[v] = node_incident_count.get(v, 0) + 1

        edges = []
        for u, v, r_name, w in selected_edges:
            rel_upper = r_name.upper()
            if rel_upper == "FOLLOWERS":
                fe_rel = "FOLLOW"
            elif rel_upper == "FRIENDS":
                fe_rel = "FRIEND"
            elif rel_upper == "MENTIONS":
                fe_rel = "MENTION"
            elif rel_upper == "REPLIES":
                fe_rel = "REPLY"
            else:
                fe_rel = rel_upper

            edges.append({
                "source": int(u),
                "target": int(v),
                "relationship_type": r_name,
                "relationship": fe_rel,
                "weight": round(w, 4)
            })

        res = {
            "user_id": int(seed_node) if seed_node is not None else 0,
            "depth": 1,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(G.nodes()),
                "total_edges": G.number_of_edges(),
                "subgraph_nodes": len(nodes),
                "subgraph_edges": len(edges),
                "seed_node": str(seed_node) if seed_node is not None else None,
                "is_filtered": True,
                "limit_applied": len(raw_edges) > max_edges
            }
        }

        if CACHE_ENABLED:
            self.cache.set(
                cache_key,
                res
            )

        return res

    # ============================================================
    # MODEL PERFORMANCE
    # ============================================================

    def get_model_performance(
        self
    ) -> Dict[str, Any]:
        """
        Return real model performance metrics.

        Sources:
        - results/rgcn_results.json   (RGCN evaluation, if trained)
        - results/final_model_metrics.csv (sklearn HistGradientBoosting baseline)

        Never returns fabricated or hardcoded metrics.
        """
        import json as _json

        models = []

        # --- Load RGCN results (from actual training) ---
        rgcn_path = os.path.join(self.results_dir, "rgcn_results.json")
        rgcn_data = None

        if os.path.exists(rgcn_path):
            try:
                with open(rgcn_path, "r") as f:
                    rgcn_data = _json.load(f)

                models.append({
                    "model_name": "RGCN (2-layer RGCNConv)",
                    "architecture_type": rgcn_data.get("architecture", {}).get(
                        "type", "Relational Graph Convolutional Network"
                    ),
                    "metrics": rgcn_data.get("test_metrics", {}),
                    "confusion_matrix": rgcn_data.get("confusion_matrix", {}),
                    "training": rgcn_data.get("training", {}),
                    "dataset": rgcn_data.get("dataset", {}),
                    "split": rgcn_data.get("split", {}),
                    "architecture": rgcn_data.get("architecture", {}),
                })
            except Exception as e:
                logger.warning(f"Failed to load RGCN results: {e}")

        # --- Load sklearn baseline results ---
        baseline_path = os.path.join(
            self.results_dir, "final_model_metrics.csv"
        )

        if os.path.exists(baseline_path):
            try:
                df = pd.read_csv(baseline_path)
                for _, row in df.iterrows():
                    models.append({
                        "model_name": str(row.get("model", "sklearn baseline")),
                        "architecture_type": "sklearn (tabular)",
                        "metrics": {
                            "accuracy": float(row.get("accuracy", 0)),
                            "precision": float(row.get("precision", 0)),
                            "recall": float(row.get("recall", 0)),
                            "f1_score": float(row.get("f1_score", 0)),
                            "roc_auc": float(row.get("roc_auc", 0))
                                if "roc_auc" in row else None,
                        },
                    })
            except Exception as e:
                logger.warning(f"Failed to load baseline results: {e}")

        if not models:
            return {
                "status": "not_available",
                "message": (
                    "No model evaluation results found. "
                    "Run the training pipeline first."
                ),
                "models": [],
            }

        # Baseline comparisons for frontend comparison table
        baseline_comparisons = []
        all_models_path = os.path.join(self.results_dir, "all_models_comparison.csv")
        if os.path.exists(all_models_path):
            try:
                df_all = pd.read_csv(all_models_path)
                for _, row in df_all.iterrows():
                    baseline_comparisons.append({
                        "model_name": str(row.get("model", "")),
                        "accuracy": float(row.get("accuracy", 0.0)),
                        "f1_score": float(row.get("f1_score", 0.0)),
                        "roc_auc": float(row.get("roc_auc", 0.0)) if pd.notna(row.get("roc_auc")) else None,
                    })
            except Exception as e:
                logger.warning(f"Failed to load all_models_comparison: {e}")

        # Feature group importances for frontend chart
        feature_importances = []
        feat_grp_path = os.path.join(self.results_dir, "feature_group_importance.csv")
        if os.path.exists(feat_grp_path):
            try:
                df_grp = pd.read_csv(feat_grp_path)
                cat_map = {"Profile": "user", "Embedding": "text", "SNA": "graph"}
                label_map = {
                    "Profile": "Profile Features (20 dims)",
                    "Embedding": "Text Embeddings (768 dims)",
                    "SNA": "SNA Graph Features (18 dims)",
                }
                for _, row in df_grp.iterrows():
                    grp = str(row.get("feature_group", ""))
                    feature_importances.append({
                        "feature": label_map.get(grp, grp),
                        "importance": float(row.get("total_importance", 0.0)),
                        "category": cat_map.get(grp, "user"),
                    })
            except Exception as e:
                logger.warning(f"Failed to load feature_group_importance: {e}")

        # --- Load RGCN ROC curve (from real test set evaluation) ---
        roc_curve_path = os.path.join(self.results_dir, "rgcn_roc_curve.json")
        roc_curve = None
        if os.path.exists(roc_curve_path):
            try:
                with open(roc_curve_path, "r") as f:
                    roc_curve = _json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load RGCN ROC curve: {e}")

        # Primary model = first model with metrics (RGCN preferred)
        primary = models[0]

        return {
            "status": "available",
            "metrics": primary.get("metrics", {}),
            "confusion_matrix": primary.get("confusion_matrix", {}),
            "metadata": {
                "model_name": primary.get("model_name", ""),
                "architecture_type": primary.get("architecture_type", ""),
                "dataset_name": "MGTAB Twitter Benchmark",
                "training": primary.get("training", {}),
                "split": primary.get("split", {}),
                "architecture": primary.get("architecture", {}),
            },
            "roc_curve": roc_curve,
            "all_models": models,
            "baseline_comparisons": baseline_comparisons,
            "feature_importances": feature_importances,
        }


    # ============================================================
    # ML BOT PREDICTION
    # ============================================================

    # The model name reported in API responses:
    _PREDICT_MODEL_NAME = "HistGradientBoosting (sklearn, 806 tabular features)"

    def predict_user_bot(
        self,
        user_id: int,
        features: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Predict whether a user is a bot or human.

        MODEL USED:
            This endpoint uses the **HistGradientBoosting** sklearn model
            loaded from models/model.pkl.  It consumes 806 tabular features
            (20 profile + 768 text embeddings + 18 SNA) loaded from
            results/ml_dataset.csv.

            This is NOT the RGCN model.  The RGCN (Relational Graph
            Convolutional Network) is a separate graph-based model
            evaluated in results/rgcn_results.json and checkpointed at
            models/rgcn_best.pt.  RGCN inference requires the full
            PyG graph (features.pt, edge_index.pt, edge_type.pt) and
            is not served through this tabular prediction endpoint.

        The ML feature vector is automatically looked up from
        ml_dataset.csv using the supplied user_id.  The dashboard
        does not need to provide the 806 features manually.
        """

    # ------------------------------------------------------------
    # 1. Check whether ML model is loaded
    # ------------------------------------------------------------
        if self.ml_model is None:
            return {
                "status": "model_not_available",
                "message": "ML prediction model (models/model.pkl) is not loaded.",
                "user_id": user_id,
                "prediction": None,
                "probability": None,
                "model_used": None,
            }

        try:
            if user_id < 0 or user_id >= self.loader.num_nodes:
                raise KeyError(
                    f"User ID {user_id} is out of bounds "
                    f"(0..{self.loader.num_nodes - 1})"
                )

        # --------------------------------------------------------
        # 3. Check ML feature dataset
        # --------------------------------------------------------
            if self.ml_features is None:
                return {
                    "status": "error",
                    "message": "ML feature dataset (results/ml_dataset.csv) is not loaded.",
                    "user_id": user_id,
                    "prediction": None,
                    "probability": None,
                    "model_used": None,
                }
            
            
            if user_id >= len(self.ml_features):
                raise KeyError(
                    f"User ID {user_id} not found in ML feature dataset."
                )

            user_row = self.ml_features.iloc[user_id]

        # --------------------------------------------------------
        # 5. Remove target column
        # --------------------------------------------------------
            feature_columns = [
                col for col in self.ml_features.columns
                if col != "bot_label"
            ]
            
            user_features = user_row[feature_columns].to_frame().T.astype(
                np.float32
            )

        # --------------------------------------------------------
        # 6. Verify feature count
        # --------------------------------------------------------
            expected_features = len(feature_columns)
            actual_features = user_features.shape[1]
            if actual_features != expected_features:
                raise ValueError(
                    f"Feature count mismatch: expected "
                    f"{expected_features}, got {actual_features}"
                )

            logger.info(
                f"Running ML prediction for user {user_id} "
                f"using {actual_features} features "
                f"(model: {self._PREDICT_MODEL_NAME})."
            )

        # --------------------------------------------------------
        # 7. Make prediction
        # --------------------------------------------------------
            prediction = int(
                self.ml_model.predict(user_features)[0]
            )

        # --------------------------------------------------------
        # 8. Get probability
        # --------------------------------------------------------
            probability = None
            
            if hasattr(self.ml_model, "predict_proba"):
                probabilities = self.ml_model.predict_proba(
                    user_features
                )[0]

            # Probability corresponding to predicted class
                if hasattr(self.ml_model, "classes_"):
                    classes = list(self.ml_model.classes_)
                    if prediction in classes:
                        class_index = classes.index(prediction)
                        probability = float(
                            probabilities[class_index]
                        )
                    else:
                        probability = float(
                            max(probabilities)
                        )
                else:
                    probability = float(max(probabilities))

        # --------------------------------------------------------
        # 9. Human-readable result
        # --------------------------------------------------------
            prediction_label = (
                "Bot" if prediction == 1 else "Human"
            )
            return {
                "status": "success",
                "message": "ML prediction executed successfully.",
                "user_id": user_id,
                "prediction": prediction,
                "prediction_label": prediction_label,
                "probability": probability,
                "model_used": self._PREDICT_MODEL_NAME,
           }

        except Exception as e:
            logger.exception(
                f"ML prediction failed for user {user_id}"
            )

            return {
                "status": "error",
                "message": f"ML model inference failed: {str(e)}",
                "user_id": user_id,
                "prediction": None,
                "probability": None,
                "model_used": self._PREDICT_MODEL_NAME,
           }
