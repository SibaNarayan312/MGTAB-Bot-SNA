import pytest
from backend.graph_builder import MGTABGraphLoader
from backend.coordination import CoordinationAnalyzer

def test_coordination_signals():
    loader = MGTABGraphLoader("data").load_graph_data()
    analyzer = CoordinationAnalyzer(loader)
    
    res = analyzer.calculate_user_coordination(0)
    assert "coordination_score" in res
    assert 0.0 <= res["coordination_score"] <= 1.0
    assert "risk_level" in res
    assert res["risk_level"] in ["low", "moderate", "high"]
    assert "signals" in res
    assert "interpretation" in res

def test_community_coordination():
    loader = MGTABGraphLoader("data").load_graph_data()
    analyzer = CoordinationAnalyzer(loader)
    
    comm_nodes = [0, 1, 2, 3, 4]
    res = analyzer.analyze_community_coordination(comm_nodes)
    assert "avg_coordination_score" in res
    assert "risk_level" in res
    assert "suspicious_node_count" in res
