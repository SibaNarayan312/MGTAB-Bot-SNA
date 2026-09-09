import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
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

MODEL_PATH = os.path.join(
    RESULTS_DIR,
    "best_model.pkl"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("FINAL HISTGRADIENTBOOSTING MODEL EVALUATION")
print("=" * 70)

df = pd.read_csv(DATASET_PATH)

print(f"\nDataset shape: {df.shape}")


# ============================================================
# FEATURES
# ============================================================

feature_columns = (
    [f"profile_{i}" for i in range(20)]
    + [f"embedding_{i}" for i in range(768)]
    + [
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
)

X = df[feature_columns]
y = df["bot_label"]


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
print(f"Testing samples : {len(X_test)}")


# ============================================================
# TRAIN BEST MODEL
# ============================================================

print("\n========== TRAINING MODEL ==========")

model = HistGradientBoostingClassifier(
    max_iter=200,
    learning_rate=0.1,
    max_leaf_nodes=31,
    random_state=42
)

model.fit(X_train, y_train)

print("HistGradientBoosting training complete.")


# ============================================================
# PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n========== FINAL METRICS ==========")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Human",
            "Bot"
        ]
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\n========== CONFUSION MATRIX ==========")
print(cm)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Human", "Bot"]
)

disp.plot()

plt.title(
    "HistGradientBoosting Confusion Matrix"
)

plt.tight_layout()

cm_path = os.path.join(
    RESULTS_DIR,
    "confusion_matrix.png"
)

plt.savefig(
    cm_path,
    dpi=300
)

plt.close()

print(f"Saved: {cm_path}")


# ============================================================
# ROC CURVE
# ============================================================

fpr, tpr, thresholds = roc_curve(
    y_test,
    y_probability
)

plt.figure(figsize=(8, 6))

plt.plot(
    fpr,
    tpr,
    label=f"HistGradientBoosting (AUC = {roc_auc:.4f})"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title(
    "ROC Curve - Bot Detection"
)

plt.legend()

plt.tight_layout()

roc_path = os.path.join(
    RESULTS_DIR,
    "roc_curve.png"
)

plt.savefig(
    roc_path,
    dpi=300
)

plt.close()

print(f"Saved: {roc_path}")


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)

print(f"\nSaved trained model to:")
print(MODEL_PATH)


# ============================================================
# SAVE METRICS
# ============================================================

metrics_df = pd.DataFrame([
    {
        "model": "HistGradientBoosting",
        "features": 806,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc
    }
])

metrics_path = os.path.join(
    RESULTS_DIR,
    "final_model_metrics.csv"
)

metrics_df.to_csv(
    metrics_path,
    index=False
)

print(f"Saved metrics to:")
print(metrics_path)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("FINAL MODEL EVALUATION COMPLETE")
print("=" * 70)