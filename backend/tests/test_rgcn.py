"""
RGCN model and checkpoint tests for MGTAB-Bot-SNA.

Tests cover:
  - Model architecture instantiation
  - Checkpoint loading from models/rgcn_best.pt
  - Forward pass and inference output shapes
  - Persisted metrics in results/rgcn_results.json
  - Parameter count consistency
"""

import json
import os
import pytest
import torch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ml.rgcn_model import RGCNBotDetector


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "models", "rgcn_best.pt")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "results", "rgcn_results.json")


# =================================================================
# Architecture Tests
# =================================================================

def test_rgcn_model_instantiates():
    """RGCNBotDetector can be instantiated with MGTAB defaults."""
    model = RGCNBotDetector(
        in_channels=788,
        hidden_channels=64,
        out_channels=2,
        num_relations=7,
        num_bases=4,
        dropout=0.3,
    )
    assert isinstance(model, RGCNBotDetector)
    assert model.in_channels == 788
    assert model.hidden_channels == 64
    assert model.out_channels == 2
    assert model.num_relations == 7


def test_rgcn_forward_pass_shape():
    """Forward pass produces [N, 2] logits for N nodes."""
    model = RGCNBotDetector()
    model.eval()

    N = 10
    x = torch.randn(N, 788)
    edge_index = torch.tensor(
        [[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long
    )
    edge_type = torch.tensor([0, 1, 2, 3], dtype=torch.long)

    with torch.no_grad():
        out = model(x, edge_index, edge_type)

    assert out.shape == (N, 2), f"Expected ({N}, 2), got {out.shape}"


def test_rgcn_get_embeddings_shape():
    """get_embeddings returns [N, hidden_channels]."""
    model = RGCNBotDetector(hidden_channels=64)
    model.eval()

    N = 5
    x = torch.randn(N, 788)
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
    edge_type = torch.tensor([0, 0], dtype=torch.long)

    with torch.no_grad():
        emb = model.get_embeddings(x, edge_index, edge_type)

    assert emb.shape == (N, 64)


def test_rgcn_count_parameters():
    """Model should have a non-trivial number of parameters."""
    model = RGCNBotDetector()
    param_count = model.count_parameters()
    assert param_count > 10000, \
        f"Expected >10k trainable params, got {param_count}"


# =================================================================
# Checkpoint Tests
# =================================================================

@pytest.mark.skipif(
    not os.path.exists(CHECKPOINT_PATH),
    reason="Checkpoint file not found at models/rgcn_best.pt",
)
def test_checkpoint_loads():
    """models/rgcn_best.pt loads successfully and contains expected keys."""
    ckpt = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
    assert "model_state_dict" in ckpt
    assert "epoch" in ckpt
    assert ckpt["epoch"] == 24


@pytest.mark.skipif(
    not os.path.exists(CHECKPOINT_PATH),
    reason="Checkpoint file not found at models/rgcn_best.pt",
)
def test_checkpoint_restores_model():
    """Checkpoint state_dict can be loaded into a fresh RGCNBotDetector."""
    model = RGCNBotDetector(
        in_channels=788,
        hidden_channels=64,
        out_channels=2,
        num_relations=7,
        num_bases=4,
        dropout=0.3,
    )
    ckpt = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    # Verify inference produces valid output
    x = torch.randn(3, 788)
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.long)
    edge_type = torch.tensor([0, 1, 2], dtype=torch.long)

    with torch.no_grad():
        out = model(x, edge_index, edge_type)
        probs = torch.softmax(out, dim=1)

    assert out.shape == (3, 2)
    assert torch.allclose(probs.sum(dim=1), torch.ones(3), atol=1e-5)


# =================================================================
# Persisted Results Tests
# =================================================================

@pytest.mark.skipif(
    not os.path.exists(RESULTS_PATH),
    reason="Results file not found at results/rgcn_results.json",
)
def test_rgcn_results_verified_metrics():
    """results/rgcn_results.json must contain the verified RGCN metrics."""
    with open(RESULTS_PATH, "r") as f:
        data = json.load(f)

    metrics = data["test_metrics"]

    assert abs(metrics["accuracy"] - 0.8578) < 0.001
    assert abs(metrics["precision"] - 0.6796) < 0.001
    assert abs(metrics["recall"] - 0.8945) < 0.001
    assert abs(metrics["f1_score"] - 0.7724) < 0.001
    assert abs(metrics["roc_auc"] - 0.9415) < 0.001


@pytest.mark.skipif(
    not os.path.exists(RESULTS_PATH),
    reason="Results file not found at results/rgcn_results.json",
)
def test_rgcn_results_no_fabricated_claims():
    """Results file must not reference Node2Vec, attention, or fabricated versions."""
    with open(RESULTS_PATH, "r") as f:
        raw = f.read()

    assert "Node2Vec" not in raw
    assert "Multi-Head Edge Attention" not in raw
    assert "v2.4.1" not in raw


@pytest.mark.skipif(
    not os.path.exists(RESULTS_PATH),
    reason="Results file not found at results/rgcn_results.json",
)
def test_rgcn_results_architecture_metadata():
    """Architecture metadata must accurately describe a 2-layer RGCNConv."""
    with open(RESULTS_PATH, "r") as f:
        data = json.load(f)

    arch = data["architecture"]
    assert arch["layers"] == 2
    assert arch["input_dim"] == 788
    assert arch["hidden_dim"] == 64
    assert arch["output_dim"] == 2
    assert arch["num_relations"] == 7
    assert "RGCNConv" in arch["implementation"]


@pytest.mark.skipif(
    not os.path.exists(RESULTS_PATH),
    reason="Results file not found at results/rgcn_results.json",
)
def test_rgcn_results_confusion_matrix():
    """Confusion matrix in results must match verified values."""
    with open(RESULTS_PATH, "r") as f:
        data = json.load(f)

    cm = data["confusion_matrix"]
    assert cm["true_negative"] == 629
    assert cm["false_positive"] == 116
    assert cm["false_negative"] == 29
    assert cm["true_positive"] == 246
