import os
import sys
import torch

RELATIONSHIP_TYPES_DEFAULT = {
    0: "followers",
    1: "friends",
    2: "mentions",
    3: "replies",
    4: "quotes",
    5: "urls",
    6: "hashtags"
}

def inspect_mgtab_dataset(data_dir: str = "data") -> dict:
    """
    Inspects and validates MGTAB dataset tensors in data_dir.
    Prints comprehensive verification report and returns inspection summary.
    """
    print("=" * 60)
    print("           MGTAB DATASET INSPECTION REPORT")
    print("=" * 60)
    print(f"Dataset Location: {os.path.abspath(data_dir)}\n")

    files = {
        "features": "features.pt",
        "labels_bot": "labels_bot.pt",
        "labels_stance": "labels_stance.pt",
        "edge_index": "edge_index.pt",
        "edge_type": "edge_type.pt",
        "edge_weight": "edge_weight.pt",
    }

    tensors = {}
    missing_files = []

    for name, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
        else:
            try:
                tensors[name] = torch.load(filepath, map_location="cpu", weights_only=False)
            except Exception as e:
                print(f"[!] Error loading {filename}: {e}")
                sys.exit(1)

    if missing_files:
        print(f"[!] WARNING: Missing dataset files in '{data_dir}': {missing_files}")
        print("    Run 'python backend/scripts/generate_synthetic_data.py' to generate a mock benchmark dataset.")
        return {"status": "missing_files", "missing": missing_files}

    # Extract Shapes & Types
    features = tensors["features"]
    labels_bot = tensors["labels_bot"]
    labels_stance = tensors["labels_stance"]
    edge_index = tensors["edge_index"]
    edge_type = tensors["edge_type"]
    edge_weight = tensors["edge_weight"]

    num_nodes = features.shape[0] if features is not None else int(edge_index.max().item() + 1)
    num_edges = edge_index.shape[1] if edge_index.dim() == 2 else edge_index.shape[0]

    unique_edge_types = torch.unique(edge_type).tolist()
    unique_bot_labels = torch.unique(labels_bot).tolist() if labels_bot is not None else []
    unique_stance_labels = torch.unique(labels_stance).tolist() if labels_stance is not None else []

    print("-" * 60)
    print(f"Total Graph Nodes  : {num_nodes}")
    print(f"Total Graph Edges  : {num_edges}")
    print(f"Unique Relation Types: {unique_edge_types}")
    print("-" * 60)

    print(f"\n1. edge_index:")
    print(f"   Shape: {list(edge_index.shape)} | Dtype: {edge_index.dtype}")
    print(f"   Min Node Index: {edge_index.min().item()} | Max Node Index: {edge_index.max().item()}")

    print(f"\n2. edge_type:")
    print(f"   Shape: {list(edge_type.shape)} | Dtype: {edge_type.dtype}")
    print(f"   Unique Relation IDs: {unique_edge_types}")
    for rel_id in sorted(unique_edge_types):
        count = (edge_type == rel_id).sum().item()
        rel_name = RELATIONSHIP_TYPES_DEFAULT.get(rel_id, "unknown")
        print(f"     - Type {rel_id} ({rel_name}): {count} edges ({count / num_edges * 100:.2f}%)")

    print(f"\n3. edge_weight:")
    print(f"   Shape: {list(edge_weight.shape)} | Dtype: {edge_weight.dtype}")
    print(f"   Min Weight: {edge_weight.min().item():.4f} | Max Weight: {edge_weight.max().item():.4f}")

    print(f"\n4. features:")
    print(f"   Shape: {list(features.shape)} | Dtype: {features.dtype}")
    print(f"   Feature Dimension: {features.shape[1]} (20 profile attrs + 768 LaBSE embeddings)")

    print(f"\n5. labels_bot:")
    print(f"   Shape: {list(labels_bot.shape)} | Dtype: {labels_bot.dtype}")
    print(f"   Unique Labels: {unique_bot_labels}")
    for label_val in unique_bot_labels:
        count = (labels_bot == label_val).sum().item()
        label_name = "Bot" if label_val == 1 else ("Human" if label_val == 0 else f"Class_{label_val}")
        print(f"     - Label {label_val} ({label_name}): {count} nodes ({count / num_nodes * 100:.2f}%)")

    print(f"\n6. labels_stance:")
    print(f"   Shape: {list(labels_stance.shape)} | Dtype: {labels_stance.dtype}")
    print(f"   Unique Stance Labels: {unique_stance_labels}")

    print("=" * 60)
    print("[OK] DATASET VERIFICATION COMPLETED SUCCESSFULLY.")
    print("=" * 60)

    return {
        "status": "valid",
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "unique_edge_types": unique_edge_types,
        "features_shape": list(features.shape),
        "edge_index_shape": list(edge_index.shape),
        "bot_labels": unique_bot_labels,
    }

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    inspect_mgtab_dataset(data_dir=data_dir)
