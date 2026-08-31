import pytest
from fastapi.testclient import TestClient
from backend.api import app

def test_api_health():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["graph_loaded"] is True

def test_api_statistics():
    with TestClient(app) as client:
        res = client.get("/statistics")
        assert res.status_code == 200
        data = res.json()
        assert data["nodes"] > 0
        assert "relationship_types" in data

def test_api_user_endpoint():
    with TestClient(app) as client:
        res = client.get("/user/0")
        assert res.status_code == 200
        data = res.json()
        assert data["user_id"] == 0
        assert "degree" in data
        assert "pagerank" in data
        assert "coordination_score" in data

def test_api_user_network_endpoint():
    with TestClient(app) as client:
        res = client.get("/user/0/network?depth=1&max_nodes=30")
        assert res.status_code == 200
        data = res.json()
        assert data["user_id"] == 0
        assert "nodes" in data
        assert "edges" in data

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

def test_api_predict_endpoint():
    with TestClient(app) as client:
        res = client.post("/predict", json={"user_id": 0})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "model_not_available"
