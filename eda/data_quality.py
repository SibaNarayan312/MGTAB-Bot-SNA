import torch

# ==========================================
# DATASET PATH
# ==========================================

DATASET_PATH = "dataset"


# ==========================================
# LOAD DATA
# ==========================================

features = torch.load(
    f"{DATASET_PATH}/features.pt",
    weights_only=False
)

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

bot_labels = torch.load(
    f"{DATASET_PATH}/labels_bot.pt",
    weights_only=False
)

stance_labels = torch.load(
    f"{DATASET_PATH}/labels_stance.pt",
    weights_only=False
)


# ==========================================
# BASIC INFORMATION
# ==========================================

print("========== DATA QUALITY CHECK ==========")

num_nodes = features.shape[0]
num_features = features.shape[1]
num_edges = edge_index.shape[1]

print("\n========== BASIC INFORMATION ==========")

print("Number of nodes:", num_nodes)
print("Number of features:", num_features)
print("Number of edges:", num_edges)

print("Feature dtype:", features.dtype)
print("Edge index dtype:", edge_index.dtype)
print("Edge type dtype:", edge_type.dtype)
print("Edge weight dtype:", edge_weight.dtype)
print("Bot label dtype:", bot_labels.dtype)
print("Stance label dtype:", stance_labels.dtype)


# ==========================================
# 1. NAN / MISSING VALUES
# ==========================================

print("\n========== MISSING / NaN VALUES ==========")

feature_nan_count = torch.isnan(features).sum().item()

print("NaN values in features:", feature_nan_count)

if feature_nan_count == 0:
    print("Missing value check: PASS")
else:
    print("Missing value check: FAIL")


# ==========================================
# 2. INFINITE VALUES
# ==========================================

print("\n========== INFINITE VALUES ==========")

feature_inf_count = torch.isinf(features).sum().item()

print("Infinite values in features:", feature_inf_count)

if feature_inf_count == 0:
    print("Infinite value check: PASS")
else:
    print("Infinite value check: FAIL")


# ==========================================
# 3. EDGE CONSISTENCY
# ==========================================

print("\n========== EDGE CONSISTENCY ==========")

print("Edges in edge_index:", edge_index.shape[1])
print("Edge types:", edge_type.shape[0])
print("Edge weights:", edge_weight.shape[0])

if (
    edge_index.shape[1]
    == edge_type.shape[0]
    == edge_weight.shape[0]
):
    print("Edge consistency: PASS")
else:
    print("Edge consistency: FAIL")


# ==========================================
# 4. NODE ID VALIDATION
# ==========================================

print("\n========== NODE ID VALIDATION ==========")

min_node_id = edge_index.min().item()
max_node_id = edge_index.max().item()

print("Minimum node ID:", min_node_id)
print("Maximum node ID:", max_node_id)
print("Expected minimum node ID: 0")
print("Expected maximum node ID:", num_nodes - 1)

if min_node_id >= 0 and max_node_id < num_nodes:
    print("Node ID validation: PASS")
else:
    print("Node ID validation: FAIL")


# ==========================================
# 5. LABEL VALIDATION
# ==========================================

print("\n========== LABEL VALIDATION ==========")

bot_unique = torch.unique(bot_labels)
stance_unique = torch.unique(stance_labels)

print("Unique bot labels:", bot_unique.tolist())
print("Unique stance labels:", stance_unique.tolist())

if set(bot_unique.tolist()) <= {0, 1}:
    print("Bot label validation: PASS")
else:
    print("Bot label validation: FAIL")

if set(stance_unique.tolist()) <= {0, 1, 2}:
    print("Stance label validation: PASS")
else:
    print("Stance label validation: FAIL")


# ==========================================
# 6. NODE / LABEL CONSISTENCY
# ==========================================

print("\n========== NODE / LABEL CONSISTENCY ==========")

print("Feature rows:", features.shape[0])
print("Bot labels:", bot_labels.shape[0])
print("Stance labels:", stance_labels.shape[0])

if (
    features.shape[0]
    == bot_labels.shape[0]
    == stance_labels.shape[0]
):
    print("Node-label consistency: PASS")
else:
    print("Node-label consistency: FAIL")


# ==========================================
# 7. EDGE TYPE VALIDATION
# ==========================================

print("\n========== EDGE TYPE VALIDATION ==========")

unique_edge_types = torch.unique(edge_type)

print("Unique edge types:", unique_edge_types.tolist())

expected_edge_types = {0, 1, 2, 3, 4, 5, 6}

if set(unique_edge_types.tolist()) <= expected_edge_types:
    print("Edge type validation: PASS")
else:
    print("Edge type validation: FAIL")


# ==========================================
# 8. EDGE WEIGHT VALIDATION
# ==========================================

print("\n========== EDGE WEIGHT VALIDATION ==========")

print("Minimum edge weight:", edge_weight.min().item())
print("Maximum edge weight:", edge_weight.max().item())
print("Mean edge weight:", edge_weight.float().mean().item())

edge_weight_nan = torch.isnan(edge_weight).sum().item()
edge_weight_inf = torch.isinf(edge_weight).sum().item()

print("NaN edge weights:", edge_weight_nan)
print("Infinite edge weights:", edge_weight_inf)

if edge_weight_nan == 0 and edge_weight_inf == 0:
    print("Edge weight validation: PASS")
else:
    print("Edge weight validation: FAIL")


# ==========================================
# 9. FEATURE STATISTICS
# ==========================================

print("\n========== FEATURE STATISTICS ==========")

print("Minimum feature value:", features.min().item())
print("Maximum feature value:", features.max().item())
print("Mean feature value:", features.mean().item())
print("Standard deviation:", features.std().item())


# ==========================================
# 10. CONSTANT FEATURES
# ==========================================

print("\n========== CONSTANT FEATURES ==========")

# Calculate standard deviation for every feature
feature_std = features.std(dim=0)

constant_features = torch.where(feature_std == 0)[0]

print("Number of constant features:", len(constant_features))

if len(constant_features) == 0:
    print("Constant feature check: PASS")
else:
    print("Constant feature check: REVIEW")


# ==========================================
# 11. BOT CLASS DISTRIBUTION
# ==========================================

print("\n========== BOT CLASS DISTRIBUTION ==========")

bot_counts = torch.bincount(bot_labels)

total_bot_samples = bot_labels.shape[0]

for label, count in enumerate(bot_counts):

    percentage = (
        count.item()
        / total_bot_samples
        * 100
    )

    if label == 0:
        label_name = "Human"
    elif label == 1:
        label_name = "Bot"
    else:
        label_name = "Unknown"

    print(
        f"Class {label} ({label_name}): "
        f"{count.item()} "
        f"({percentage:.2f}%)"
    )


# ==========================================
# 12. STANCE CLASS DISTRIBUTION
# ==========================================

print("\n========== STANCE CLASS DISTRIBUTION ==========")

stance_counts = torch.bincount(stance_labels)

total_stance_samples = stance_labels.shape[0]

stance_names = {
    0: "Neutral",
    1: "Against",
    2: "Support"
}

for label, count in enumerate(stance_counts):

    percentage = (
        count.item()
        / total_stance_samples
        * 100
    )

    label_name = stance_names.get(
        label,
        "Unknown"
    )

    print(
        f"Class {label} ({label_name}): "
        f"{count.item()} "
        f"({percentage:.2f}%)"
    )


# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n========== DATA QUALITY CHECK COMPLETE ==========")

print("Dataset is ready for further analysis")
print("after reviewing the checks above.")