import torch

# ==========================================
# DATASET PATH
# ==========================================

DATASET_PATH = "dataset"


# ==========================================
# LOAD DATASET
# ==========================================

edge_index = torch.load(
    f"{DATASET_PATH}/edge_index.pt",
    weights_only=False
)

edge_type = torch.load(
    f"{DATASET_PATH}/edge_type.pt",
    weights_only=False
)

edge_weight = torch.load(
    f"{DATASET_PATH}/edge_weight.pt",
    weights_only=False
)

features = torch.load(
    f"{DATASET_PATH}/features.pt",
    weights_only=False
)

bot_labels = torch.load(
    f"{DATASET_PATH}/labels_bot.pt",
    weights_only=False
)

stance_labels = torch.load(
    f"{DATASET_PATH}/labels_stance.pt",
    weights_only=False
)


# ==========================================
# BASIC DATASET INFORMATION
# ==========================================

print("========== DATASET INFORMATION ==========")

print("Features shape:", features.shape)
print("Edge index shape:", edge_index.shape)
print("Edge type shape:", edge_type.shape)
print("Edge weight shape:", edge_weight.shape)
print("Bot labels shape:", bot_labels.shape)
print("Stance labels shape:", stance_labels.shape)


# ==========================================
# LABEL DISTRIBUTION
# ==========================================

print("\n========== LABEL DISTRIBUTION ==========")

print("\nBot label distribution:")
print(torch.bincount(bot_labels))

print("\nStance label distribution:")
print(torch.bincount(stance_labels))


# ==========================================
# FEATURES
# ==========================================

print("\n========== FEATURES ==========")

print("Type:", type(features))
print("Dtype:", features.dtype)
print("Number of dimensions:", features.ndim)
print("Shape:", features.shape)

print("\nFirst 10 feature values of first node:")
print(features[0][:10])

print("\nFeature value range:")
print("Min:", features.min().item())
print("Max:", features.max().item())


# ==========================================
# EDGE INDEX
# ==========================================

print("\n========== EDGE INDEX ==========")

print("Type:", type(edge_index))
print("Dtype:", edge_index.dtype)
print("Number of dimensions:", edge_index.ndim)
print("Shape:", edge_index.shape)

print("\nFirst 10 edges:")
print(edge_index[:, :10])

print("\nMinimum node ID:", edge_index.min().item())
print("Maximum node ID:", edge_index.max().item())


# ==========================================
# EDGE TYPE
# ==========================================

print("\n========== EDGE TYPE ==========")

print("Dtype:", edge_type.dtype)
print("Shape:", edge_type.shape)

print("\nFirst 20 edge types:")
print(edge_type[:20])

print("\nUnique edge types:")
print(torch.unique(edge_type))


# ==========================================
# EDGE WEIGHT
# ==========================================

print("\n========== EDGE WEIGHT ==========")

print("Dtype:", edge_weight.dtype)
print("Shape:", edge_weight.shape)

print("\nFirst 20 edge weights:")
print(edge_weight[:20])

print("\nWeight statistics:")
print("Min:", edge_weight.min().item())
print("Max:", edge_weight.max().item())
print("Mean:", edge_weight.float().mean().item())


# ==========================================
# BOT LABELS
# ==========================================

print("\n========== BOT LABELS ==========")

print("Dtype:", bot_labels.dtype)
print("Shape:", bot_labels.shape)

print("\nUnique values:")
print(torch.unique(bot_labels))

print("\nFirst 20 labels:")
print(bot_labels[:20])


# ==========================================
# STANCE LABELS
# ==========================================

print("\n========== STANCE LABELS ==========")

print("Dtype:", stance_labels.dtype)
print("Shape:", stance_labels.shape)

print("\nUnique values:")
print(torch.unique(stance_labels))

print("\nFirst 20 labels:")
print(stance_labels[:20])