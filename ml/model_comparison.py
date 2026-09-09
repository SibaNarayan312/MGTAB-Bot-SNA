import os
import time

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
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

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("ML MODEL COMPARISON")
print("=" * 70)

print("\nLoading ML dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset shape: {df.shape}")


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


# ============================================================
# INPUT / TARGET
# ============================================================

X = df[feature_columns]
y = df["bot_label"]

print("\n========== FEATURE INFORMATION ==========")
print(f"Total features: {X.shape[1]}")
print(f"Total samples: {X.shape[0]}")


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n========== DATA SPLIT ==========")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

print("\nTraining class distribution:")
print(y_train.value_counts().sort_index())

print("\nTesting class distribution:")
print(y_test.value_counts().sort_index())


# ============================================================
# DEFINE MODELS
# ============================================================

models = {

    "Logistic Regression": Pipeline([
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
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),

    "HistGradientBoosting": HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.1,
        max_leaf_nodes=31,
        random_state=42
    )
}


# ============================================================
# TRAIN AND EVALUATE
# ============================================================

results = []

for model_name, model in models.items():

    print("\n" + "=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    start_time = time.time()

    print("\nTraining...")

    model.fit(
        X_train,
        y_train
    )

    training_time = time.time() - start_time

    print(
        f"Training completed in "
        f"{training_time:.2f} seconds"
    )

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    y_pred = model.predict(X_test)

    # --------------------------------------------------------
    # METRICS
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

    # --------------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------------

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    # --------------------------------------------------------
    # CLASSIFICATION REPORT
    # --------------------------------------------------------

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
        "model": model_name,
        "num_features": X.shape[1],
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "training_time_seconds": training_time
    })


# ============================================================
# RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "f1_score",
    ascending=False
).reset_index(drop=True)


# ============================================================
# SAVE RESULTS
# ============================================================

output_path = os.path.join(
    RESULTS_DIR,
    "model_comparison.csv"
)

results_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# FINAL COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("FINAL MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)

print(
    f"\nResults saved to:"
    f"\n{output_path}"
)


# ============================================================
# BEST MODEL
# ============================================================

best_model = results_df.iloc[0]

print("\n========== BEST MODEL ==========")

print(
    f"Model    : {best_model['model']}"
)

print(
    f"Accuracy : {best_model['accuracy']:.4f}"
)

print(
    f"Precision: {best_model['precision']:.4f}"
)

print(
    f"Recall   : {best_model['recall']:.4f}"
)

print(
    f"F1-score : {best_model['f1_score']:.4f}"
)

print("\n" + "=" * 70)
print("MODEL COMPARISON COMPLETE")
print("=" * 70)