import pytest
import pandas as pd
from backend.graph_builder import MGTABGraphLoader
from backend.sna import SNAAnalyzer

def test_sna_node_metrics():
    loader = MGTABGraphLoader("data").load_graph_data()
    analyzer = SNAAnalyzer(loader)
    metrics = analyzer.calculate_node_metrics()
    
    assert len(metrics) == loader.num_nodes
    assert 0 in metrics
    user_0 = metrics[0]
    assert "degree" in user_0
    assert "in_degree" in user_0
    assert "out_degree" in user_0
    assert "pagerank" in user_0
    assert "clustering_coefficient" in user_0
    assert user_0["pagerank"] >= 0.0

def test_sna_relation_statistics():
    loader = MGTABGraphLoader("data").load_graph_data()
    analyzer = SNAAnalyzer(loader)
    rel_stats = analyzer.calculate_relation_statistics()
    
    assert len(rel_stats) == 7
    assert "followers" in rel_stats
    assert "mentions" in rel_stats
    assert rel_stats["mentions"]["number_of_edges"] >= 0

def test_sna_dataframe_export():
    loader = MGTABGraphLoader("data").load_graph_data()
    analyzer = SNAAnalyzer(loader)
    df = analyzer.to_dataframe()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == loader.num_nodes
    assert "user_id" in df.columns
    assert "pagerank" in df.columns
