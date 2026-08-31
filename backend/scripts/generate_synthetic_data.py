import os
import argparse
import torch

def generate_synthetic_mgtab(output_dir: str = "data", num_nodes: int = 1000, num_edges: int = 8000, seed: int = 42):
    """
    Generates synthetic MGTAB dataset tensors matching official MGTAB benchmark semantics:
    - features.pt: [num_nodes, 788] float32 tensor
    - labels_bot.pt: [num_nodes] int64 binary labels (0: human, 1: bot)
    - labels_stance.pt: [num_nodes] int64 stance labels (0, 1, 2)
    - edge_index.pt: [2, num_edges] int64 tensor
    - edge_type.pt: [num_edges] int64 tensor (0..6 relation types)
    - edge_weight.pt: [num_edges] float32 tensor
    """
    torch.manual_seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    print(f"[+] Generating synthetic MGTAB dataset with {num_nodes} nodes and {num_edges} edges...")

    # Node features: 788 features (20 profile + 768 LaBSE embeddings)
    features = torch.randn((num_nodes, 788), dtype=torch.float32)

    # Bot labels: ~25% bots (1), 75% humans (0)
    labels_bot = torch.bernoulli(torch.full((num_nodes,), 0.25)).to(torch.int64)

    # Stance labels: 0 (against), 1 (neutral), 2 (support)
    labels_stance = torch.randint(0, 3, (num_nodes,), dtype=torch.int64)

    # Edge Index: random directed edges between nodes
    sources = torch.randint(0, num_nodes, (num_edges,), dtype=torch.int64)
    targets = torch.randint(0, num_nodes, (num_edges,), dtype=torch.int64)
    
    # Avoid self-loops for simple representation, though multi-graphs allow them
    mask = sources != targets
    sources = sources[mask]
    targets = targets[mask]
    actual_edges = sources.shape[0]

    edge_index = torch.stack([sources, targets], dim=0)

    # Edge Types: 7 categories (0: followers, 1: friends, 2: mentions, 3: replies, 4: quotes, 5: urls, 6: hashtags)
    # Give higher frequency to followers (0), friends (1), mentions (2)
    probs = torch.tensor([0.25, 0.25, 0.20, 0.10, 0.05, 0.08, 0.07])
    edge_type = torch.multinomial(probs, actual_edges, replacement=True).to(torch.int64)

    # Edge Weights: interaction counts or similarity scores (1.0 to 10.0)
    edge_weight = torch.randint(1, 10, (actual_edges,), dtype=torch.float32)

    # Save tensors
    torch.save(features, os.path.join(output_dir, "features.pt"))
    torch.save(labels_bot, os.path.join(output_dir, "labels_bot.pt"))
    torch.save(labels_stance, os.path.join(output_dir, "labels_stance.pt"))
    torch.save(edge_index, os.path.join(output_dir, "edge_index.pt"))
    torch.save(edge_type, os.path.join(output_dir, "edge_type.pt"))
    torch.save(edge_weight, os.path.join(output_dir, "edge_weight.pt"))

    print(f"[OK] Synthetic MGTAB dataset successfully saved to '{output_dir}/'.")
    print(f"    - Nodes: {num_nodes}")
    print(f"    - Edges: {actual_edges}")
    print(f"    - Feature shape: {features.shape}")
    print(f"    - Edge index shape: {edge_index.shape}")
    print(f"    - Unique edge types: {torch.unique(edge_type).tolist()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic MGTAB Dataset Generator")
    parser.add_argument("--output_dir", type=str, default="data", help="Output directory path")
    parser.add_argument("--nodes", type=int, default=1000, help="Number of nodes")
    parser.add_argument("--edges", type=int, default=8000, help="Number of edges")
    args = parser.parse_args()

    generate_synthetic_mgtab(output_dir=args.output_dir, num_nodes=args.nodes, num_edges=args.edges)
