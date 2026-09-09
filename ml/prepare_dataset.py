import os
import torch
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("PREPARING ML DATASET")
print("=" * 60)

print("\nLoading PyTorch dataset...")

features = torch.load(
    os.path.join(DATASET_DIR, "features.pt"),
    weights_only=False
)

bot_labels = torch.load(
    os.path.join(DATASET_DIR, "labels_bot.pt"),
    weights_only=False
)

print(f"Original features shape: {features.shape}")
print(f"Bot labels shape: {bot_labels.shape}")


# ============================================================
# CONVERT TO NUMPY
# ============================================================

features_np = features.detach().cpu().numpy()
bot_labels_np = bot_labels.detach().cpu().numpy()


# ============================================================
# SEPARATE PROFILE AND TEXT EMBEDDING FEATURES
# ============================================================

PROFILE_FEATURES = 20

profile_features = features_np[:, :PROFILE_FEATURES]
text_embeddings = features_np[:, PROFILE_FEATURES:]


print("\n========== FEATURE STRUCTURE ==========")

print(f"Profile features: {profile_features.shape}")
print(f"Text embeddings: {text_embeddings.shape}")


# ============================================================
# LOAD SNA FEATURES
# ============================================================

print("\nLoading SNA features...")

sna_path = os.path.join(
    RESULTS_DIR,
    "sna_features.csv"
)

sna_df = pd.read_csv(sna_path)

print(f"SNA dataframe shape: {sna_df.shape}")

print("\nSNA columns:")
print(sna_df.columns.tolist())


# ============================================================
# VALIDATE USER COUNT
# ============================================================

if len(features_np) != len(sna_df):
    raise ValueError(
        f"Node count mismatch: "
        f"dataset has {len(features_np)} users but "
        f"SNA features have {len(sna_df)} users."
    )


# ============================================================
# VALIDATE USER IDs
# ============================================================

expected_user_ids = np.arange(len(features_np))

actual_user_ids = sna_df["user_id"].to_numpy()

if not np.array_equal(expected_user_ids, actual_user_ids):
    raise ValueError(
        "SNA user_id values do not match dataset node IDs."
    )

print("\nUser ID validation: PASS")


# ============================================================
# REMOVE USER ID
# ============================================================

sna_features_df = sna_df.drop(columns=["user_id"])

print(
    f"SNA ML features: "
    f"{sna_features_df.shape[1]}"
)


# ============================================================
# CONVERT SNA FEATURES TO NUMPY
# ============================================================

sna_features = sna_features_df.to_numpy(
    dtype=np.float32
)


# ============================================================
# COMBINE ALL FEATURES
# ============================================================

combined_features = np.concatenate(
    [
        profile_features,
        text_embeddings,
        sna_features
    ],
    axis=1
)


print("\n========== FINAL FEATURE MATRIX ==========")

print(
    f"Profile features: {profile_features.shape[1]}"
)

print(
    f"Text embedding features: {text_embeddings.shape[1]}"
)

print(
    f"SNA features: {sna_features.shape[1]}"
)

print(
    f"Total ML features: {combined_features.shape[1]}"
)

print(
    f"Number of users: {combined_features.shape[0]}"
)


# ============================================================
# CHECK DATA QUALITY
# ============================================================

print("\n========== DATA QUALITY ==========")

nan_count = np.isnan(combined_features).sum()
inf_count = np.isinf(combined_features).sum()

print(f"NaN values: {nan_count}")
print(f"Infinite values: {inf_count}")

if nan_count != 0 or inf_count != 0:
    raise ValueError(
        "Combined feature matrix contains NaN or infinite values."
    )

print("Feature quality check: PASS")


# ============================================================
# CREATE FEATURE NAMES
# ============================================================

profile_names = [
    f"profile_{i}"
    for i in range(20)
]

embedding_names = [
    f"embedding_{i}"
    for i in range(768)
]

sna_names = sna_features_df.columns.tolist()

feature_names = (
    profile_names
    + embedding_names
    + sna_names
)


# ============================================================
# CREATE FINAL DATAFRAME
# ============================================================

ml_df = pd.DataFrame(
    combined_features,
    columns=feature_names
)

ml_df["bot_label"] = bot_labels_np


# ============================================================
# SAVE DATASET
# ============================================================

output_path = os.path.join(
    RESULTS_DIR,
    "ml_dataset.csv"
)

ml_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n========== ML DATASET SUMMARY ==========")

print(f"Output file: {output_path}")
print(f"Dataset shape: {ml_df.shape}")

print("\nClass distribution:")

print(
    ml_df["bot_label"]
    .value_counts()
    .sort_index()
)

print("\nExpected:")
print("0 = Human")
print("1 = Bot")

print("\nFirst 5 rows:")
print(ml_df.head())

print("\n" + "=" * 60)
print("ML DATASET PREPARATION COMPLETE")
print("=" * 60)