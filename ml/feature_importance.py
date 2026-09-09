import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "results",
    "ml_dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "results",
    "best_model.pkl"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("MODEL FEATURE IMPORTANCE ANALYSIS")
print("=" * 70)

df = pd.read_csv(DATASET_PATH)

model = joblib.load(MODEL_PATH)

print(f"\nDataset shape: {df.shape}")
print("Model loaded successfully.")


# ============================================================
# FEATURE COLUMNS
# ============================================================

profile_features = [
    f"profile_{i}"
    for i in range(20)
]

embedding_features = [
    f"embedding_{i}"
    for i in range(768)
]

sna_features = [
    "degree",
    "in_degree",
    "out_degree",
    "weighted_degree",
    "degree_centrality",
    "pagerank",
    "betweenness",
    "clustering_coefficient",
    "followers_degree",
    "friends_degree",
    "mentions_degree",
    "replies_degree",
    "quotes_degree",
    "urls_degree",
    "hashtags_degree",
    "community_id",
    "community_size",
    "coordination_score"
]

feature_columns = (
    profile_features
    + embedding_features
    + sna_features
)

X = df[feature_columns]
y = df["bot_label"]


# ============================================================
# SAME TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# PERMUTATION IMPORTANCE
# ============================================================

print("\n========== PERMUTATION IMPORTANCE ==========")

print("Calculating feature importance...")
print("This may take a little time.")

importance = permutation_importance(
    model,
    X_test,
    y_test,
    n_repeats=5,
    random_state=42,
    scoring="f1",
    n_jobs=-1
)


# ============================================================
# CREATE IMPORTANCE DATAFRAME
# ============================================================

importance_df = pd.DataFrame({
    "feature": feature_columns,
    "importance_mean": importance.importances_mean,
    "importance_std": importance.importances_std
})

importance_df = importance_df.sort_values(
    "importance_mean",
    ascending=False
).reset_index(drop=True)


# ============================================================
# TOP 30 FEATURES
# ============================================================

print("\n========== TOP 30 FEATURES ==========")

print(
    importance_df.head(30).to_string(
        index=False
    )
)


# ============================================================
# SAVE ALL FEATURE IMPORTANCE
# ============================================================

importance_path = os.path.join(
    RESULTS_DIR,
    "feature_importance.csv"
)

importance_df.to_csv(
    importance_path,
    index=False
)

print(
    f"\nSaved complete feature importance to:"
    f"\n{importance_path}"
)


# ============================================================
# FEATURE GROUP IMPORTANCE
# ============================================================

print("\n========== FEATURE GROUP ANALYSIS ==========")

importance_df["feature_group"] = importance_df["feature"].apply(
    lambda x:
        "Profile"
        if x.startswith("profile_")
        else
        "Embedding"
        if x.startswith("embedding_")
        else
        "SNA"
)


group_importance = (
    importance_df
    .groupby("feature_group")["importance_mean"]
    .sum()
    .sort_values(ascending=False)
)


print("\nTotal permutation importance by feature group:")

print(group_importance)


# ============================================================
# SAVE GROUP IMPORTANCE
# ============================================================

group_path = os.path.join(
    RESULTS_DIR,
    "feature_group_importance.csv"
)

group_importance.reset_index(
    name="total_importance"
).to_csv(
    group_path,
    index=False
)

print(
    f"\nSaved group importance to:"
    f"\n{group_path}"
)


# ============================================================
# TOP 20 FEATURE PLOT
# ============================================================

top_20 = importance_df.head(20).sort_values(
    "importance_mean"
)

plt.figure(figsize=(10, 8))

plt.barh(
    top_20["feature"],
    top_20["importance_mean"]
)

plt.xlabel("Permutation Importance")
plt.ylabel("Feature")

plt.title(
    "Top 20 Features - HistGradientBoosting"
)

plt.tight_layout()

plot_path = os.path.join(
    RESULTS_DIR,
    "top_20_feature_importance.png"
)

plt.savefig(
    plot_path,
    dpi=300
)

plt.close()

print(
    f"\nSaved feature importance plot to:"
    f"\n{plot_path}"
)


# ============================================================
# GROUP IMPORTANCE PLOT
# ============================================================

plt.figure(figsize=(8, 6))

plt.bar(
    group_importance.index,
    group_importance.values
)

plt.xlabel("Feature Group")
plt.ylabel("Total Permutation Importance")

plt.title(
    "Feature Group Importance"
)

plt.tight_layout()

group_plot_path = os.path.join(
    RESULTS_DIR,
    "feature_group_importance.png"
)

plt.savefig(
    group_plot_path,
    dpi=300
)

plt.close()

print(
    f"Saved group importance plot to:"
    f"\n{group_plot_path}"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE ANALYSIS COMPLETE")
print("=" * 70)