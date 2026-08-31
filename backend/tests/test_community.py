import pytest
from backend.graph_builder import MGTABGraphLoader
from backend.community import CommunityDetector

def test_community_detection():
    loader = MGTABGraphLoader("data").load_graph_data()
    detector = CommunityDetector(loader)
    comm_map = detector.detect_communities()
    
    assert len(comm_map) == loader.num_nodes
    assert 0 in comm_map
    assert isinstance(comm_map[0], int)

def test_community_statistics():
    loader = MGTABGraphLoader("data").load_graph_data()
    detector = CommunityDetector(loader)
    detector.detect_communities()
    stats = detector.calculate_community_statistics()
    
    assert len(stats) > 0
    first_comm_id = list(stats.keys())[0]
    first_comm = stats[first_comm_id]
    
    assert "community_id" in first_comm
    assert "size" in first_comm
    assert "density" in first_comm
    assert "top_nodes" in first_comm
    assert "relationship_distribution" in first_comm
