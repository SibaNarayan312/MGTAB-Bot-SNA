import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


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


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("ML BASELINE EXPERIMENT")
print("=" * 60)

df = pd.read_csv(DATASET_PATH)

print(f"\nDataset shape: {df.shape}")


# ============================================================
# TARGET
# ============================================================

y = df["bot_label"]


# ============================================================
# DEFINE FEATURE GROUPS
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


# ============================================================
# EXPERIMENTS
# ============================================================

experiments = {
    "Profile Only": profile_features,

    "Profile + Embeddings":
        profile_features + embedding_features,

    "Profile + Embeddings + SNA":
        profile_features + embedding_features + sna_features
}


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

indices = df.index

train_indices, test_indices = train_test_split(
    indices,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n========== DATA SPLIT ==========")

print(f"Training samples: {len(train_indices)}")
print(f"Testing samples: {len(test_indices)}")

print("\nTraining class distribution:")
print(
    y.iloc[train_indices]
    .value_counts()
    .sort_index()
)

print("\nTesting class distribution:")
print(
    y.iloc[test_indices]
    .value_counts()
    .sort_index()
)


# ============================================================
# RUN EXPERIMENTS
# ============================================================

results = []


for experiment_name, feature_columns in experiments.items():

    print("\n" + "=" * 60)
    print(experiment_name)
    print("=" * 60)

    X = df[feature_columns]

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]

    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]

    print(f"Number of features: {X.shape[1]}")

    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    print("\nTraining Logistic Regression...")

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    y_pred = model.predict(X_test)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    print("\n========== RESULTS ==========")

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Human",
                "Bot"
            ],
            zero_division=0
        )
    )

    results.append({
        "experiment": experiment_name,
        "num_features": X.shape[1],
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    })


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

output_path = os.path.join(
    BASE_DIR,
    "results",
    "baseline_results.csv"
)

results_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("BASELINE EXPERIMENT SUMMARY")
print("=" * 60)

print(
    results_df.to_string(
        index=False
    )
)

print(
    f"\nSaved results to: {output_path}"
)

print("\n" + "=" * 60)
print("BASELINE EXPERIMENT COMPLETE")
print("=" * 60)