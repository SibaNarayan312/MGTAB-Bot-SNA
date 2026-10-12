"""
RGCN Training Pipeline for MGTAB Bot Detection
================================================

End-to-end training and evaluation of a Relational Graph Convolutional
Network (RGCN) for binary bot detection on the MGTAB benchmark.

Usage:
    python -m ml.rgcn_train
    python ml/rgcn_train.py

Phases:
    1. Data loading and verification
    2. Graph construction (PyG Data object)
    3. Stratified train/val/test split
    4. Model initialization
    5. Training with early stopping
    6. Evaluation on held-out test set
    7. Results export and baseline comparison
"""

import os
import sys
import json
import time
import random
import warnings

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.optim import Adam

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import StratifiedShuffleSplit

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.rgcn_model import RGCNBotDetector


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Paths
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# Model hyperparameters
HIDDEN_CHANNELS = 64
NUM_BASES = 4
DROPOUT = 0.3

# Training hyperparameters
LEARNING_RATE = 0.01
WEIGHT_DECAY = 5e-4
MAX_EPOCHS = 200
PATIENCE = 30           # Early stopping patience

# Split ratios
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10


# ============================================================
# REPRODUCIBILITY
# ============================================================

def set_seeds(seed: int = SEED):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ============================================================
# PHASE 1  -- DATA LOADING AND VERIFICATION
# ============================================================

def load_and_verify_data(dataset_dir: str = DATASET_DIR):
    """
    Load all MGTAB tensors and verify their shapes, dtypes, and alignment.
    """
    print("=" * 70)
    print("PHASE 1: DATA LOADING AND VERIFICATION")
    print("=" * 70)

    tensor_files = {
        "features": "features.pt",
        "edge_index": "edge_index.pt",
        "edge_type": "edge_type.pt",
        "edge_weight": "edge_weight.pt",
        "labels_bot": "labels_bot.pt",
    }

    tensors = {}
    for name, filename in tensor_files.items():
        path = os.path.join(dataset_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required tensor: {path}")
        tensors[name] = torch.load(path, map_location="cpu", weights_only=False)
        print(f"  Loaded {filename:20s} -> shape={str(tensors[name].shape):25s} dtype={tensors[name].dtype}")

    features = tensors["features"]
    edge_index = tensors["edge_index"]
    edge_type = tensors["edge_type"]
    edge_weight = tensors["edge_weight"]
    labels = tensors["labels_bot"]

    num_nodes = features.shape[0]
    num_features = features.shape[1]
    num_edges = edge_index.shape[1]
    num_relations = int(edge_type.max().item()) + 1

    # Verification checks
    print(f"\n  Verification:")
    print(f"    Node count        : {num_nodes}")
    print(f"    Feature dimension : {num_features}")
    print(f"    Edge count        : {num_edges}")
    print(f"    Relation types    : {num_relations}")

    assert edge_index.shape[0] == 2, f"edge_index must be [2, E], got {edge_index.shape}"
    assert edge_type.shape[0] == num_edges, f"edge_type length {edge_type.shape[0]} != num_edges {num_edges}"
    assert edge_weight.shape[0] == num_edges, f"edge_weight length {edge_weight.shape[0]} != num_edges {num_edges}"
    assert labels.shape[0] == num_nodes, f"labels length {labels.shape[0]} != num_nodes {num_nodes}"

    assert edge_index.min() >= 0, f"edge_index min < 0: {edge_index.min()}"
    assert edge_index.max() < num_nodes, f"edge_index max >= num_nodes: {edge_index.max()} >= {num_nodes}"

    # Label distribution
    unique_labels, label_counts = labels.unique(return_counts=True)
    print(f"\n  Label distribution:")
    for lbl, cnt in zip(unique_labels.tolist(), label_counts.tolist()):
        label_name = "Human" if lbl == 0 else "Bot"
        print(f"    {lbl} ({label_name}): {cnt} ({cnt/num_nodes*100:.1f}%)")

    # Self-loop analysis
    self_loop_mask = edge_index[0] == edge_index[1]
    num_self_loops = self_loop_mask.sum().item()
    print(f"\n  Self-loops: {num_self_loops} ({num_self_loops/num_edges*100:.1f}% of all edges)")

    # Edge type distribution
    print(f"\n  Edge type distribution:")
    relation_names = {
        0: "followers", 1: "friends", 2: "mentions",
        3: "replies", 4: "quotes", 5: "urls", 6: "hashtags"
    }
    et_unique, et_counts = edge_type.unique(return_counts=True)
    for t, c in zip(et_unique.tolist(), et_counts.tolist()):
        print(f"    Type {t} ({relation_names.get(t, 'unknown'):10s}): {c:>10,} edges")

    # Edge weight range
    print(f"\n  Edge weight range: [{edge_weight.min().item():.6f}, {edge_weight.max().item():.6f}]")

    print(f"\n  [OK] All verification checks passed.")

    return features, edge_index, edge_type, edge_weight, labels


# ============================================================
# PHASE 2  -- GRAPH CONSTRUCTION
# ============================================================

def build_pyg_data(features, edge_index, edge_type, edge_weight, labels):
    """
    Construct a PyTorch Geometric Data object.

    SELF-LOOP DECISION:
        The MGTAB dataset contains 205,819 self-loops (12.1% of edges).
        These are KEPT because:
        1. Self-loops in GCN-style models act as skip connections,
           allowing each node to retain its own features during
           message passing. GCN (Kipf & Welling, 2017) explicitly
           adds self-loops for this reason.
        2. In the MGTAB context, self-loops may encode meaningful
           self-referential relationships (e.g., a user sharing their
           own content via URLs/hashtags).
        3. Removing them would discard 12% of the graph signal without
           clear justification.

    EDGE WEIGHT DECISION:
        PyG's RGCNConv (v2.8.0) does NOT accept edge_weight in its
        forward() method. The signature is:
            forward(x, edge_index, edge_type)
        Therefore edge weights are stored in the Data object for
        reference but are NOT used during message passing. This is
        a limitation of the current RGCNConv implementation, not a
        design choice. Edge weights remain available for future use
        if a custom RGCN layer is implemented.
    """
    print("\n" + "=" * 70)
    print("PHASE 2: GRAPH CONSTRUCTION")
    print("=" * 70)

    from torch_geometric.data import Data

    data = Data(
        x=features.float(),
        edge_index=edge_index.long(),
        edge_type=edge_type.long(),
        edge_weight=edge_weight.float(),
        y=labels.long(),
    )

    data.num_relations = int(edge_type.max().item()) + 1

    # Verify self-loops are present
    self_loops = (data.edge_index[0] == data.edge_index[1]).sum().item()
    print(f"  Created PyG Data object:")
    print(f"    Nodes       : {data.num_nodes}")
    print(f"    Edges       : {data.num_edges}")
    print(f"    Features    : {data.num_node_features}")
    print(f"    Relations   : {data.num_relations}")
    print(f"    Self-loops  : {self_loops} (KEPT  -- see docstring for rationale)")
    print(f"    Edge weights: stored but NOT used by RGCNConv (unsupported)")

    return data


# ============================================================
# PHASE 3  -- TRAIN/VALIDATION/TEST SPLIT
# ============================================================

def create_stratified_split(data, train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO,
                            test_ratio=TEST_RATIO, seed=SEED):
    """
    Create reproducible stratified train/val/test node masks.

    The split preserves bot/human ratio across all subsets.
    """
    print("\n" + "=" * 70)
    print("PHASE 3: STRATIFIED TRAIN/VAL/TEST SPLIT")
    print("=" * 70)

    num_nodes = data.num_nodes
    labels = data.y.numpy()
    indices = np.arange(num_nodes)

    # First split: train vs (val+test)
    sss1 = StratifiedShuffleSplit(
        n_splits=1,
        test_size=(val_ratio + test_ratio),
        random_state=seed,
    )
    train_idx, temp_idx = next(sss1.split(indices, labels))

    # Second split: val vs test (from the remaining)
    temp_labels = labels[temp_idx]
    relative_test = test_ratio / (val_ratio + test_ratio)
    sss2 = StratifiedShuffleSplit(
        n_splits=1,
        test_size=relative_test,
        random_state=seed,
    )
    val_rel_idx, test_rel_idx = next(sss2.split(temp_idx, temp_labels))
    val_idx = temp_idx[val_rel_idx]
    test_idx = temp_idx[test_rel_idx]

    # Create boolean masks
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)

    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True

    data.train_mask = train_mask
    data.val_mask = val_mask
    data.test_mask = test_mask

    # Verify no overlap
    assert (train_mask & val_mask).sum() == 0, "Train/val overlap!"
    assert (train_mask & test_mask).sum() == 0, "Train/test overlap!"
    assert (val_mask & test_mask).sum() == 0, "Val/test overlap!"
    assert (train_mask | val_mask | test_mask).all(), "Some nodes unassigned!"

    # Print split statistics
    for split_name, mask in [("Train", train_mask), ("Val", val_mask), ("Test", test_mask)]:
        split_labels = data.y[mask]
        n = mask.sum().item()
        n_human = (split_labels == 0).sum().item()
        n_bot = (split_labels == 1).sum().item()
        print(f"  {split_name:5s}: {n:6,} nodes | Human: {n_human:5,} ({n_human/n*100:.1f}%) | Bot: {n_bot:5,} ({n_bot/n*100:.1f}%)")

    # Save split indices for reproducibility
    split_info = {
        "seed": seed,
        "train_ratio": train_ratio,
        "val_ratio": val_ratio,
        "test_ratio": test_ratio,
        "train_count": int(train_mask.sum()),
        "val_count": int(val_mask.sum()),
        "test_count": int(test_mask.sum()),
        "train_indices": train_idx.tolist(),
        "val_indices": val_idx.tolist(),
        "test_indices": test_idx.tolist(),
    }
    split_path = os.path.join(RESULTS_DIR, "rgcn_split.json")
    with open(split_path, "w") as f:
        json.dump(split_info, f, indent=2)
    print(f"\n  Split info saved to: {split_path}")

    return data


# ============================================================
# PHASE 4  -- TRAINING
# ============================================================

def train_epoch(model, data, optimizer, class_weights=None):
    """Train for one epoch. Returns training loss and accuracy."""
    model.train()
    optimizer.zero_grad()

    out = model(data.x, data.edge_index, data.edge_type)

    loss = F.cross_entropy(
        out[data.train_mask],
        data.y[data.train_mask],
        weight=class_weights,
    )
    loss.backward()
    optimizer.step()

    pred = out[data.train_mask].argmax(dim=1)
    acc = (pred == data.y[data.train_mask]).float().mean().item()

    return loss.item(), acc


@torch.no_grad()
def evaluate(model, data, mask):
    """Evaluate model on a given mask. Returns loss, accuracy, and predictions."""
    model.eval()

    out = model(data.x, data.edge_index, data.edge_type)
    loss = F.cross_entropy(out[mask], data.y[mask]).item()

    probs = F.softmax(out[mask], dim=1)
    pred = probs.argmax(dim=1)
    acc = (pred == data.y[mask]).float().mean().item()

    return loss, acc, pred.cpu(), probs[:, 1].cpu()


def train_rgcn(model, data, device=DEVICE):
    """
    Full training loop with early stopping and best-model checkpointing.
    """
    print("\n" + "=" * 70)
    print("PHASE 5: TRAINING")
    print("=" * 70)

    model = model.to(device)
    data = data.to(device)

    print(f"\n  Device: {device}")
    print(f"  Model:\n{model}")
    print(f"\n  Trainable parameters: {model.count_parameters():,}")

    # Compute class weights to handle imbalance
    train_labels = data.y[data.train_mask]
    n_human = (train_labels == 0).sum().float()
    n_bot = (train_labels == 1).sum().float()
    total = n_human + n_bot
    class_weights = torch.tensor(
        [total / (2.0 * n_human), total / (2.0 * n_bot)],
        device=device,
    )
    print(f"  Class weights: Human={class_weights[0]:.4f}, Bot={class_weights[1]:.4f}")

    optimizer = Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    print(f"\n  Optimizer   : Adam (lr={LEARNING_RATE}, weight_decay={WEIGHT_DECAY})")
    print(f"  Max epochs  : {MAX_EPOCHS}")
    print(f"  Patience    : {PATIENCE}")
    print(f"  Loss        : CrossEntropy (class-weighted)")

    # Training loop
    best_val_f1 = 0.0
    best_val_loss = float("inf")
    best_epoch = 0
    patience_counter = 0
    history = []

    checkpoint_path = os.path.join(MODELS_DIR, "rgcn_best.pt")
    os.makedirs(MODELS_DIR, exist_ok=True)

    print(f"\n  {'Epoch':>5s} | {'Train Loss':>10s} | {'Train Acc':>9s} | {'Val Loss':>8s} | {'Val Acc':>7s} | {'Val F1':>7s} | {'Status':>10s}")
    print(f"  {'-'*5} | {'-'*10} | {'-'*9} | {'-'*8} | {'-'*7} | {'-'*7} | {'-'*10}")

    start_time = time.time()

    for epoch in range(1, MAX_EPOCHS + 1):
        train_loss, train_acc = train_epoch(model, data, optimizer, class_weights)

        val_loss, val_acc, val_pred, val_probs = evaluate(model, data, data.val_mask)
        val_labels = data.y[data.val_mask].cpu()
        val_f1 = f1_score(val_labels, val_pred, zero_division=0)

        status = ""

        # Check for improvement
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            status = "* best"

            # Save checkpoint
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_f1": val_f1,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "hyperparameters": {
                    "hidden_channels": HIDDEN_CHANNELS,
                    "num_bases": NUM_BASES,
                    "dropout": DROPOUT,
                    "learning_rate": LEARNING_RATE,
                    "weight_decay": WEIGHT_DECAY,
                    "seed": SEED,
                },
            }, checkpoint_path)
        else:
            patience_counter += 1

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "val_f1": val_f1,
        })

        # Print every 10 epochs, first 5, and on best/stop
        if epoch <= 5 or epoch % 10 == 0 or status or patience_counter >= PATIENCE:
            print(f"  {epoch:5d} | {train_loss:10.4f} | {train_acc:9.4f} | {val_loss:8.4f} | {val_acc:7.4f} | {val_f1:7.4f} | {status:>10s}")

        # Early stopping
        if patience_counter >= PATIENCE:
            print(f"\n  Early stopping at epoch {epoch} (no improvement for {PATIENCE} epochs)")
            break

    elapsed = time.time() - start_time
    print(f"\n  Training complete in {elapsed:.1f}s")
    print(f"  Best epoch: {best_epoch} (Val F1={best_val_f1:.4f}, Val Loss={best_val_loss:.4f})")
    print(f"  Checkpoint saved: {checkpoint_path}")

    # Save training history
    history_path = os.path.join(RESULTS_DIR, "rgcn_training_history.csv")
    pd.DataFrame(history).to_csv(history_path, index=False)
    print(f"  Training history saved: {history_path}")

    return model, checkpoint_path, history


# ============================================================
# PHASE 6  -- TEST EVALUATION
# ============================================================

def evaluate_on_test(model, data, checkpoint_path, device=DEVICE):
    """
    Load best model checkpoint and evaluate on the untouched test set.
    """
    print("\n" + "=" * 70)
    print("PHASE 6: TEST SET EVALUATION")
    print("=" * 70)

    # Load best checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    data = data.to(device)
    best_epoch = checkpoint["epoch"]

    print(f"  Loaded best checkpoint from epoch {best_epoch}")

    # Evaluate on test set
    test_loss, test_acc, test_pred, test_probs = evaluate(model, data, data.test_mask)
    test_labels = data.y[data.test_mask].cpu()

    # Compute metrics
    accuracy = accuracy_score(test_labels, test_pred)
    precision = precision_score(test_labels, test_pred, zero_division=0)
    recall_val = recall_score(test_labels, test_pred, zero_division=0)
    f1 = f1_score(test_labels, test_pred, zero_division=0)

    try:
        roc_auc = roc_auc_score(test_labels, test_probs)
    except ValueError:
        roc_auc = float("nan")
        warnings.warn("Could not compute ROC-AUC (single class in test set?)")

    cm = confusion_matrix(test_labels, test_pred)

    print(f"\n  ========== RGCN TEST RESULTS ==========")
    print(f"  Accuracy  : {accuracy:.4f}")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall_val:.4f}")
    print(f"  F1-Score  : {f1:.4f}")
    print(f"  ROC-AUC   : {roc_auc:.4f}")

    print(f"\n  Confusion Matrix:")
    print(f"                Predicted")
    print(f"              Human   Bot")
    print(f"  Actual Human  {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"  Actual Bot    {cm[1][0]:5d}  {cm[1][1]:5d}")

    print(f"\n  Classification Report:")
    print(classification_report(
        test_labels, test_pred,
        target_names=["Human", "Bot"],
        digits=4,
    ))

    # Save results
    results = {
        "model": "RGCN (RGCNConv, 2-layer)",
        "architecture": {
            "type": "Relational Graph Convolutional Network",
            "implementation": "torch_geometric.nn.RGCNConv",
            "layers": 2,
            "input_dim": model.in_channels,
            "hidden_dim": model.hidden_channels,
            "output_dim": model.out_channels,
            "num_relations": model.num_relations,
            "num_bases": model.num_bases,
            "dropout": model.dropout,
            "activation": "ReLU",
            "normalization": "BatchNorm1d",
        },
        "training": {
            "optimizer": "Adam",
            "learning_rate": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "max_epochs": MAX_EPOCHS,
            "early_stopping_patience": PATIENCE,
            "best_epoch": best_epoch,
            "loss_function": "CrossEntropy (class-weighted)",
            "seed": SEED,
            "device": str(device),
        },
        "dataset": {
            "name": "MGTAB",
            "num_nodes": int(data.num_nodes),
            "num_edges": int(data.num_edges),
            "num_features": int(data.num_node_features),
            "num_relations": int(data.num_relations),
            "self_loops": int((data.edge_index[0] == data.edge_index[1]).sum()),
            "self_loops_decision": "KEPT (self-loops act as skip connections in GCN)",
            "edge_weights_used": False,
            "edge_weights_reason": "RGCNConv (PyG 2.8.0) does not accept edge_weight parameter",
        },
        "split": {
            "method": "StratifiedShuffleSplit",
            "train_ratio": TRAIN_RATIO,
            "val_ratio": VAL_RATIO,
            "test_ratio": TEST_RATIO,
            "seed": SEED,
            "train_count": int(data.train_mask.sum()),
            "val_count": int(data.val_mask.sum()),
            "test_count": int(data.test_mask.sum()),
        },
        "test_metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall_val),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc),
        },
        "confusion_matrix": {
            "true_negative": int(cm[0][0]),
            "false_positive": int(cm[0][1]),
            "false_negative": int(cm[1][0]),
            "true_positive": int(cm[1][1]),
        },
        "trainable_parameters": model.count_parameters(),
    }

    results_path = os.path.join(RESULTS_DIR, "rgcn_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved: {results_path}")

    # Also save as CSV for comparison
    metrics_csv = pd.DataFrame([{
        "model": "RGCN (2-layer RGCNConv)",
        "features": model.in_channels,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall_val,
        "f1_score": f1,
        "roc_auc": roc_auc,
    }])
    csv_path = os.path.join(RESULTS_DIR, "rgcn_test_metrics.csv")
    metrics_csv.to_csv(csv_path, index=False)
    print(f"  Metrics CSV saved: {csv_path}")

    return results


# ============================================================
# PHASE 7  -- BASELINE COMPARISON
# ============================================================

def compare_with_baselines(rgcn_results):
    """
    Compare RGCN results against existing verified sklearn baselines.
    """
    print("\n" + "=" * 70)
    print("PHASE 7: BASELINE COMPARISON")
    print("=" * 70)

    # Load existing baseline results
    comparison_path = os.path.join(RESULTS_DIR, "model_comparison.csv")
    final_metrics_path = os.path.join(RESULTS_DIR, "final_model_metrics.csv")

    baselines = []

    if os.path.exists(comparison_path):
        df = pd.read_csv(comparison_path)
        for _, row in df.iterrows():
            baselines.append({
                "model": row["model"],
                "accuracy": row["accuracy"],
                "precision": row["precision"],
                "recall": row["recall"],
                "f1_score": row["f1_score"],
                "roc_auc": row.get("roc_auc", None),
            })

    if os.path.exists(final_metrics_path):
        df = pd.read_csv(final_metrics_path)
        for _, row in df.iterrows():
            # Update existing entry with ROC-AUC from final metrics
            for b in baselines:
                if b["model"] == row["model"] and b.get("roc_auc") is None:
                    b["roc_auc"] = row.get("roc_auc", None)

    # Add RGCN
    rgcn_metrics = rgcn_results["test_metrics"]
    baselines.append({
        "model": "RGCN (2-layer)",
        "accuracy": rgcn_metrics["accuracy"],
        "precision": rgcn_metrics["precision"],
        "recall": rgcn_metrics["recall"],
        "f1_score": rgcn_metrics["f1_score"],
        "roc_auc": rgcn_metrics["roc_auc"],
    })

    # Print comparison table
    print(f"\n  {'Model':<30s} | {'Accuracy':>8s} | {'Precision':>9s} | {'Recall':>6s} | {'F1':>7s} | {'ROC-AUC':>7s}")
    print(f"  {'-'*30} | {'-'*8} | {'-'*9} | {'-'*6} | {'-'*7} | {'-'*7}")
    for b in baselines:
        roc = f"{b['roc_auc']:.4f}" if b.get("roc_auc") is not None else "  N/A"
        print(f"  {b['model']:<30s} | {b['accuracy']:8.4f} | {b['precision']:9.4f} | {b['recall']:6.4f} | {b['f1_score']:7.4f} | {roc:>7s}")

    # Save combined comparison
    comparison_df = pd.DataFrame(baselines)
    combined_path = os.path.join(RESULTS_DIR, "all_models_comparison.csv")
    comparison_df.to_csv(combined_path, index=False)
    print(f"\n  Combined comparison saved: {combined_path}")

    # Determine best model
    best = max(baselines, key=lambda b: b["f1_score"])
    print(f"\n  Best model by F1: {best['model']} (F1={best['f1_score']:.4f})")

    if best["model"].startswith("RGCN"):
        print("   ->  RGCN outperforms sklearn baselines on F1 score.")
    else:
        print(f"   ->  {best['model']} still outperforms RGCN on F1 score.")
        print("    Note: RGCN operates directly on graph structure via message passing,")
        print("    while sklearn baselines use pre-computed SNA features on top of profile+embeddings.")

    return baselines


# ============================================================
# MAIN
# ============================================================

def main():
    """Run the complete RGCN training and evaluation pipeline."""
    total_start = time.time()

    print("\n" + "#" * 70)
    print("#  MGTAB RGCN BOT DETECTION  -- TRAINING PIPELINE")
    print("#" * 70)

    set_seeds(SEED)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Phase 1: Load data
    features, edge_index, edge_type, edge_weight, labels = load_and_verify_data()

    # Phase 2: Build PyG graph
    data = build_pyg_data(features, edge_index, edge_type, edge_weight, labels)

    # Phase 3: Create split
    data = create_stratified_split(data)

    # Phase 4: Initialize model
    print("\n" + "=" * 70)
    print("PHASE 4: MODEL INITIALIZATION")
    print("=" * 70)

    model = RGCNBotDetector(
        in_channels=data.num_node_features,
        hidden_channels=HIDDEN_CHANNELS,
        out_channels=2,
        num_relations=data.num_relations,
        num_bases=NUM_BASES,
        dropout=DROPOUT,
    )
    print(f"\n{model}")

    # Phase 5: Train
    model, checkpoint_path, history = train_rgcn(model, data, DEVICE)

    # Phase 6: Evaluate on test set
    rgcn_results = evaluate_on_test(model, data, checkpoint_path, DEVICE)

    # Phase 7: Compare with baselines
    compare_with_baselines(rgcn_results)

    total_elapsed = time.time() - total_start
    print("\n" + "#" * 70)
    print(f"#  PIPELINE COMPLETE  -- Total time: {total_elapsed:.1f}s")
    print("#" * 70)


if __name__ == "__main__":
    main()
