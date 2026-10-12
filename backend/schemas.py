from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Health Check Response
# ============================================================

class HealthResponse(BaseModel):
    status: str = Field(
        ...,
        json_schema_extra={"example": "healthy"}
    )

    graph_loaded: bool = Field(
        ...,
        json_schema_extra={"example": True}
    )

    num_nodes: int = Field(
        ...,
        json_schema_extra={"example": 1000}
    )

    num_edges: int = Field(
        ...,
        json_schema_extra={"example": 7990}
    )


# ============================================================
# Statistics Response
# ============================================================

class GraphStatisticsResponse(BaseModel):
    nodes: int = Field(
        ...,
        json_schema_extra={"example": 1000}
    )

    edges: int = Field(
        ...,
        json_schema_extra={"example": 7990}
    )

    graph_type: str = Field(
        ...,
        json_schema_extra={"example": "directed_multigraph"}
    )

    density: float = Field(
        ...,
        json_schema_extra={"example": 0.0079}
    )

    relationship_types: Dict[str, int] = Field(
        ...,
        json_schema_extra={
            "example": {
                "mentions": 1581,
                "replies": 821
            }
        }
    )

    communities: int = Field(
        ...,
        json_schema_extra={"example": 16}
    )


# ============================================================
# User SNA Response
# ============================================================

class UserResponse(BaseModel):
    user_id: int = Field(
        ...,
        json_schema_extra={"example": 123}
    )

    degree: int = Field(
        ...,
        json_schema_extra={"example": 42}
    )

    in_degree: int = Field(
        ...,
        json_schema_extra={"example": 30}
    )

    out_degree: int = Field(
        ...,
        json_schema_extra={"example": 12}
    )

    weighted_degree: float = Field(
        ...,
        json_schema_extra={"example": 150.0}
    )

    degree_centrality: float = Field(
        ...,
        json_schema_extra={"example": 0.021}
    )

    pagerank: float = Field(
        ...,
        json_schema_extra={"example": 0.0023}
    )

    betweenness: float = Field(
        ...,
        json_schema_extra={"example": 0.0}
    )

    clustering_coefficient: float = Field(
        ...,
        json_schema_extra={"example": 0.12}
    )

    community_id: int = Field(
        ...,
        json_schema_extra={"example": 5}
    )

    community_size: int = Field(
        ...,
        json_schema_extra={"example": 120}
    )

    coordination_score: float = Field(
        ...,
        json_schema_extra={"example": 0.67}
    )

    risk_level: Optional[str] = Field(
        None,
        json_schema_extra={"example": "high"}
    )

    signals: Optional[Dict[str, float]] = Field(None)

    relationship_degrees: Optional[Dict[str, int]] = Field(None)

    bot_label: Optional[int] = Field(
        None,
        description="Ground truth bot label if present in dataset "
                    "(0: Human, 1: Bot)"
    )


# ============================================================
# Network Graph Visualization Schemas
# ============================================================

class NetworkNode(BaseModel):
    id: int
    label: str
    community_id: int
    pagerank: float
    degree: int
    bot_label: Optional[int] = None


class NetworkEdge(BaseModel):
    source: int
    target: int
    relationship_type: str
    weight: float


class UserNetworkResponse(BaseModel):
    user_id: int
    depth: int
    node_count: int
    edge_count: int
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]


# ============================================================
# Communities Response
# ============================================================

class CommunitySummary(BaseModel):
    community_id: int
    size: int
    density: float
    internal_edges: int
    external_edges: int
    top_nodes: List[int]


class CommunitiesResponse(BaseModel):
    total: int
    page: int
    page_size: int
    communities: List[CommunitySummary]


class CommunityDetailResponse(BaseModel):
    community_id: int
    size: int
    internal_edges: int
    external_edges: int
    density: float
    top_nodes: List[int]
    relationship_distribution: Dict[str, int]
    coordination_analysis: Dict[str, Any]


# ============================================================
# ML Model Prediction Endpoint Schemas
# ============================================================

class PredictionRequest(BaseModel):
    user_id: int

    features: Optional[Dict[str, float]] = None


class PredictionResponse(BaseModel):
    status: str = Field(
        ...,
        json_schema_extra={"example": "success"}
    )

    message: str = Field(
        ...,
        json_schema_extra={
            "example": "ML prediction executed successfully."
        }
    )

    user_id: int

    prediction: Optional[int] = Field(
        None,
        description="Numeric prediction: 0 = Human, 1 = Bot"
    )

    prediction_label: Optional[str] = Field(
        None,
        description="Human-readable prediction: Human or Bot"
    )

    probability: Optional[float] = Field(
        None,
        description="Probability of the predicted class"
    )

    model_used: Optional[str] = Field(
        None,
        description=(
            "Name of the model that produced this prediction. "
            "Currently: 'HistGradientBoosting (sklearn, 806 tabular features)'"
        )
    )