"""
Comprehensive API test suite for MGTAB-Bot-SNA backend.

Tests cover:
  - Health and statistics endpoints
  - User SNA endpoints (valid + invalid IDs)
  - Community endpoints (listing + detail)
  - /model-performance (loads real metrics from results/rgcn_results.json)
  - /predict (uses HistGradientBoosting via models/model.pkl, NOT RGCN)
  - Edge-case / error handling
"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app


# =================================================================
# System Endpoints
# =================================================================

def test_api_health():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["graph_loaded"] is True
        assert data["num_nodes"] > 0
        assert data["num_edges"] > 0


def test_api_statistics():
    with TestClient(app) as client:
        res = client.get("/statistics")
        assert res.status_code == 200
        data = res.json()
        assert data["nodes"] > 0
        assert "relationship_types" in data
        assert isinstance(data["relationship_types"], dict)
        assert data["density"] > 0

        # Verify enriched frontend-compatible fields
        assert data["total_users"] == data["nodes"]
        assert data["total_relationships"] == data["edges"]
        assert data["bot_count"] > 0
        assert data["human_count"] > 0
        assert data["bot_count"] + data["human_count"] == data["nodes"]
        assert 0.0 < data["bot_ratio"] < 1.0
        assert data["community_count"] == data["communities"]
        assert isinstance(data["relationship_breakdown"], list)
        assert len(data["relationship_breakdown"]) > 0
        assert isinstance(data["community_size_distribution"], list)
        assert "network" in data
        assert data["network"]["density"] == data["density"]
        assert isinstance(data["system_insights"], list)


# =================================================================
# User Endpoints
# =================================================================

def test_api_user_endpoint():
    with TestClient(app) as client:
        res = client.get("/user/0")
        assert res.status_code == 200
        data = res.json()
        assert data["user_id"] == 0
        assert "degree" in data
        assert "pagerank" in data
        assert "coordination_score" in data
        assert "community_id" in data


def test_api_user_invalid_id():
    """Requesting a user ID beyond graph bounds should return an error."""
    with TestClient(app) as client:
        res = client.get("/user/999999999")
        assert res.status_code in (404, 422, 500)


def test_api_user_network_endpoint():
    with TestClient(app) as client:
        res = client.get("/user/0/network?depth=1&max_nodes=30")
        assert res.status_code == 200
        data = res.json()
        assert data["user_id"] == 0
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert len(data["edges"]) <= 350


# =================================================================
# General Network Graph Endpoints (Bounded for Cytoscape.js)
# =================================================================

def test_api_network_endpoint_bounded_response():
    """
    /network must return bounded node and edge responses.
    Crucially, it must NEVER return 80,000+ edges that freeze Cytoscape.
    """
    with TestClient(app) as client:
        res = client.get("/network?max_nodes=100&max_edges=350")
        assert res.status_code == 200
        data = res.json()

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) <= 100
        assert len(data["edges"]) <= 350, \
            f"Edge count should be <= 350 to prevent browser lockup, got {len(data['edges'])}"

        # Verify node fields
        if data["nodes"]:
            first_node = data["nodes"][0]
            assert "id" in first_node
            assert "degree" in first_node
            assert "community_id" in first_node
            assert "prediction" in first_node
            assert first_node["prediction"] in ("BOT", "HUMAN", "UNKNOWN")

        # Verify edge fields
        if data["edges"]:
            first_edge = data["edges"][0]
            assert "source" in first_edge
            assert "target" in first_edge
            assert "relationship" in first_edge
            assert "weight" in first_edge

        # Verify metadata
        assert "metadata" in data
        assert data["metadata"]["is_filtered"] is True
        assert data["metadata"]["total_nodes"] == 10199
        assert data["metadata"]["total_edges"] == 1700108


def test_api_network_endpoint_filtered_by_prediction():
    """Filtering by BOT prediction returns only BOT nodes."""
    with TestClient(app) as client:
        res = client.get("/network?max_nodes=50&prediction=BOT")
        assert res.status_code == 200
        data = res.json()
        for node in data["nodes"]:
            assert node["prediction"] == "BOT"


def test_api_network_endpoint_filtered_by_community():
    """Filtering by community returns only nodes from that community."""
    with TestClient(app) as client:
        res = client.get("/network?max_nodes=50&community_id=0")
        assert res.status_code == 200
        data = res.json()
        for node in data["nodes"]:
            assert node["community_id"] == 0


def test_api_network_endpoint_clamped_bounds():
    """Even if an excessive max_nodes is requested, it must be capped <= 200."""
    with TestClient(app) as client:
        # Requesting 200
        res = client.get("/network?max_nodes=200")
        assert res.status_code == 200
        data = res.json()
        assert len(data["nodes"]) <= 200
        assert len(data["edges"]) <= 500


# =================================================================
# Community Endpoints
# =================================================================

def test_api_communities_endpoint():
    with TestClient(app) as client:
        res = client.get("/communities?page=1&page_size=5")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] > 0
        assert len(data["communities"]) <= 5


def test_api_community_detail_endpoint():
    with TestClient(app) as client:
        res = client.get("/community/0")
        assert res.status_code == 200
        data = res.json()
        assert data["community_id"] == 0
        assert "coordination_analysis" in data


# =================================================================
# Model Performance Endpoint
# =================================================================

def test_model_performance_returns_real_metrics():
    """
    /model-performance must return metrics loaded from
    results/rgcn_results.json — never fabricated values.
    """
    with TestClient(app) as client:
        res = client.get("/model-performance")
        assert res.status_code == 200
        data = res.json()

        # Must indicate availability
        assert data.get("status") == "available"

        # Verify RGCN metrics match the verified values
        metrics = data.get("metrics", {})
        assert abs(metrics["accuracy"] - 0.8578) < 0.001, \
            f"RGCN accuracy should be ~0.8578, got {metrics['accuracy']}"
        assert abs(metrics["precision"] - 0.6796) < 0.001
        assert abs(metrics["recall"] - 0.8945) < 0.001
        assert abs(metrics["f1_score"] - 0.7724) < 0.001
        assert abs(metrics["roc_auc"] - 0.9415) < 0.001

        # Confusion matrix must match
        cm = data.get("confusion_matrix", {})
        assert cm.get("true_negative") == 629
        assert cm.get("false_positive") == 116
        assert cm.get("false_negative") == 29
        assert cm.get("true_positive") == 246

        # Metadata must reference RGCN, not fabricated model names
        meta = data.get("metadata", {})
        assert "RGCN" in meta.get("model_name", ""), \
            f"Primary model should be RGCN, got: {meta.get('model_name')}"

        # ROC curve must be present with valid coordinates
        roc_curve = data.get("roc_curve")
        assert roc_curve is not None
        assert len(roc_curve) > 0
        assert roc_curve[0]["fpr"] == 0.0
        assert roc_curve[-1]["fpr"] == 1.0


def test_model_performance_no_fabricated_claims():
    """Ensure model-performance response doesn't contain fabricated values."""
    with TestClient(app) as client:
        res = client.get("/model-performance")
        data = res.json()
        raw = str(data)

        # These were fabricated values that must NOT appear
        assert "Node2Vec" not in raw
        assert "Multi-Head Edge Attention" not in raw
        assert "0.942" not in raw  # fabricated accuracy
        assert "0.963" not in raw  # fabricated ROC-AUC
        assert "0.906" not in raw  # fabricated F1
        assert "v2.4.1" not in raw  # fabricated version


def test_model_performance_includes_all_models():
    """
    The all_models list should contain at least the RGCN model.
    If final_model_metrics.csv exists, HistGradientBoosting
    should also appear.
    """
    with TestClient(app) as client:
        res = client.get("/model-performance")
        data = res.json()
        all_models = data.get("all_models", [])
        assert len(all_models) >= 1

        model_names = [m["model_name"] for m in all_models]
        assert any("RGCN" in name for name in model_names)


# =================================================================
# Predict Endpoint — HistGradientBoosting (NOT RGCN)
# =================================================================

def test_predict_endpoint_success():
    """
    /predict must return a genuine HistGradientBoosting prediction
    for a valid user_id, NOT 'model_not_available'.
    """
    with TestClient(app) as client:
        res = client.post("/predict", json={"user_id": 0})
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "success", \
            f"Expected 'success', got '{data['status']}': {data.get('message')}"
        assert data["prediction"] in (0, 1)
        assert data["prediction_label"] in ("Human", "Bot")
        assert isinstance(data["probability"], float)
        assert 0.0 <= data["probability"] <= 1.0


def test_predict_reports_model_used():
    """
    /predict must include model_used field identifying the
    HistGradientBoosting model, NOT the RGCN.
    """
    with TestClient(app) as client:
        res = client.post("/predict", json={"user_id": 0})
        data = res.json()
        model_used = data.get("model_used", "")

        assert "HistGradientBoosting" in model_used, \
            f"model_used should identify HistGradientBoosting, got: '{model_used}'"
        assert "RGCN" not in model_used, \
            "/predict uses sklearn, not RGCN"


def test_predict_invalid_user_id():
    """Prediction with out-of-bounds user_id should return error."""
    with TestClient(app) as client:
        res = client.post("/predict", json={"user_id": 999999999})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["prediction"] is None


def test_predict_negative_user_id():
    """Prediction with negative user_id should return error."""
    with TestClient(app) as client:
        res = client.post("/predict", json={"user_id": -1})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "error"
        assert data["prediction"] is None


def test_predict_multiple_users_consistent():
    """Multiple predictions should return consistent types."""
    with TestClient(app) as client:
        for uid in [0, 1, 5, 10]:
            res = client.post("/predict", json={"user_id": uid})
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert data["prediction"] in (0, 1)
            assert isinstance(data["probability"], float)
