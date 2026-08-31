import pytest
import networkx as nx
from backend.graph_builder import MGTABGraphLoader

def test_graph_builder_loading():
    loader = MGTABGraphLoader("data").load_graph_data()
    assert loader.num_nodes > 0
    assert loader.num_edges > 0
    assert loader.edge_index is not None
    assert loader.edge_type is not None

def test_graph_builder_multidigraph():
    loader = MGTABGraphLoader("data").load_graph_data()
    G = loader.build_multidigraph()
    assert isinstance(G, nx.MultiDiGraph)
    assert G.number_of_nodes() == loader.num_nodes
    assert G.number_of_edges() == loader.num_edges

def test_graph_builder_relation_subgraph():
    loader = MGTABGraphLoader("data").load_graph_data()
    subG = loader.get_relation_subgraph("mentions")
    assert isinstance(subG, nx.DiGraph)
    assert subG.number_of_nodes() == loader.num_nodes

def test_graph_builder_user_subgraph():
    loader = MGTABGraphLoader("data").load_graph_data()
    user_subG = loader.get_user_subgraph(user_id=0, depth=1, max_nodes=20)
    assert isinstance(user_subG, nx.MultiDiGraph)
    assert 0 in user_subG
    assert user_subG.number_of_nodes() <= 20
