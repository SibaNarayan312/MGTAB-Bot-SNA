import os
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA


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
print("TEXT EMBEDDING EDA")
print("=" * 60)

features = torch.load(
    os.path.join(DATASET_DIR, "features.pt"),
    weights_only=False
)

bot_labels = torch.load(
    os.path.join(DATASET_DIR, "labels_bot.pt"),
    weights_only=False
)


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
print(f"Total features: {features_np.shape[1]}")
print(f"Profile features: {profile_features.shape[1]}")
print(f"Text embedding features: {text_embeddings.shape[1]}")
print(f"Number of nodes: {text_embeddings.shape[0]}")


# ============================================================
# BASIC EMBEDDING STATISTICS
# ============================================================

print("\n========== EMBEDDING STATISTICS ==========")

print(f"Minimum value: {text_embeddings.min():.6f}")
print(f"Maximum value: {text_embeddings.max():.6f}")
print(f"Mean: {text_embeddings.mean():.6f}")
print(f"Standard deviation: {text_embeddings.std():.6f}")


# ============================================================
# CHECK NaN AND INFINITE VALUES
# ============================================================

print("\n========== EMBEDDING QUALITY ==========")

nan_count = np.isnan(text_embeddings).sum()
inf_count = np.isinf(text_embeddings).sum()

print(f"NaN values: {nan_count}")
print(f"Infinite values: {inf_count}")

if nan_count == 0 and inf_count == 0:
    print("Embedding quality check: PASS")
else:
    print("Embedding quality check: WARNING")


# ============================================================
# PER-DIMENSION STATISTICS
# ============================================================

embedding_means = text_embeddings.mean(axis=0)
embedding_stds = text_embeddings.std(axis=0)

print("\n========== DIMENSION STATISTICS ==========")

print(f"Average dimension mean: {embedding_means.mean():.6f}")
print(f"Average dimension std: {embedding_stds.mean():.6f}")

print(f"Minimum dimension mean: {embedding_means.min():.6f}")
print(f"Maximum dimension mean: {embedding_means.max():.6f}")

print(f"Minimum dimension std: {embedding_stds.min():.6f}")
print(f"Maximum dimension std: {embedding_stds.max():.6f}")


# ============================================================
# HUMAN VS BOT EMBEDDING MEANS
# ============================================================

human_embeddings = text_embeddings[bot_labels_np == 0]
bot_embeddings = text_embeddings[bot_labels_np == 1]

human_mean = human_embeddings.mean(axis=0)
bot_mean = bot_embeddings.mean(axis=0)

difference = bot_mean - human_mean
absolute_difference = np.abs(difference)


# ============================================================
# TOP DIFFERENT EMBEDDING DIMENSIONS
# ============================================================

top_indices = np.argsort(absolute_difference)[::-1][:20]

comparison_df = pd.DataFrame({
    "Embedding_Dimension": top_indices,
    "Human_Mean": human_mean[top_indices],
    "Bot_Mean": bot_mean[top_indices],
    "Difference_Bot_minus_Human": difference[top_indices],
    "Absolute_Difference": absolute_difference[top_indices]
})

print("\n========== TOP 20 HUMAN VS BOT EMBEDDING DIFFERENCES ==========")
print(comparison_df.to_string(index=False))


# ============================================================
# SAVE COMPARISON TABLE
# ============================================================

comparison_path = os.path.join(
    RESULTS_DIR,
    "top_embedding_differences.csv"
)

comparison_df.to_csv(comparison_path, index=False)

print(f"\nSaved: {comparison_path}")


# ============================================================
# EMBEDDING VALUE DISTRIBUTION
# ============================================================

print("\n========== EMBEDDING VALUE DISTRIBUTION ==========")

plt.figure(figsize=(10, 6))

plt.hist(
    human_embeddings.flatten(),
    bins=100,
    alpha=0.5,
    label="Human"
)

plt.hist(
    bot_embeddings.flatten(),
    bins=100,
    alpha=0.5,
    label="Bot"
)

plt.xlabel("Embedding Value")
plt.ylabel("Frequency")
plt.title("Overall Text Embedding Value Distribution")
plt.legend()
plt.tight_layout()

distribution_path = os.path.join(
    RESULTS_DIR,
    "embedding_value_distribution.png"
)

plt.savefig(distribution_path, dpi=300)
plt.show()
plt.close()

print(f"Saved: {distribution_path}")


# ============================================================
# PCA
# ============================================================

print("\n========== PCA ANALYSIS ==========")

print("Reducing 768 embedding dimensions to 2 dimensions...")

pca = PCA(n_components=2)

embedding_2d = pca.fit_transform(text_embeddings)

explained_variance = pca.explained_variance_ratio_

print(
    f"PC1 explained variance: "
    f"{explained_variance[0] * 100:.2f}%"
)

print(
    f"PC2 explained variance: "
    f"{explained_variance[1] * 100:.2f}%"
)

print(
    f"Total explained variance: "
    f"{explained_variance.sum() * 100:.2f}%"
)


# ============================================================
# PCA HUMAN VS BOT PLOT
# ============================================================

plt.figure(figsize=(10, 7))

human_mask = bot_labels_np == 0
bot_mask = bot_labels_np == 1

plt.scatter(
    embedding_2d[human_mask, 0],
    embedding_2d[human_mask, 1],
    alpha=0.35,
    s=15,
    label="Human"
)

plt.scatter(
    embedding_2d[bot_mask, 0],
    embedding_2d[bot_mask, 1],
    alpha=0.35,
    s=15,
    label="Bot"
)

plt.xlabel(
    f"PC1 ({explained_variance[0] * 100:.2f}% variance)"
)

plt.ylabel(
    f"PC2 ({explained_variance[1] * 100:.2f}% variance)"
)

plt.title("PCA of Text Embeddings: Human vs Bot")
plt.legend()
plt.tight_layout()

pca_path = os.path.join(
    RESULTS_DIR,
    "embedding_pca_human_vs_bot.png"
)

plt.savefig(pca_path, dpi=300)
plt.show()
plt.close()

print(f"Saved: {pca_path}")


# ============================================================
# PCA CLASS CENTROIDS
# ============================================================

human_pca_mean = embedding_2d[human_mask].mean(axis=0)
bot_pca_mean = embedding_2d[bot_mask].mean(axis=0)

print("\n========== PCA CLASS CENTROIDS ==========")

print(
    f"Human centroid: "
    f"({human_pca_mean[0]:.4f}, {human_pca_mean[1]:.4f})"
)

print(
    f"Bot centroid: "
    f"({bot_pca_mean[0]:.4f}, {bot_pca_mean[1]:.4f})"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("TEXT EMBEDDING EDA COMPLETE")
print("=" * 60)

print("Created:")
print("- results/top_embedding_differences.csv")
print("- results/embedding_value_distribution.png")
print("- results/embedding_pca_human_vs_bot.png")