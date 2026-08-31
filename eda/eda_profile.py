import torch
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# LOAD DATA
# ==========================================

DATASET_PATH = "dataset"

features = torch.load(
    f"{DATASET_PATH}/features.pt",
    weights_only=False
)

bot_labels = torch.load(
    f"{DATASET_PATH}/labels_bot.pt",
    weights_only=False
)

# ==========================================
# EXTRACT PROFILE FEATURES
# ==========================================

# MGTAB representation:
# First 20 features = user/profile features
# Remaining 768 = text embedding

profile_features = features[:, :20]

print("========== PROFILE FEATURE EDA ==========")

print("Total nodes:", features.shape[0])
print("Total features:", features.shape[1])
print("Profile features:", profile_features.shape[1])
print("Text embedding features:", features.shape[1] - 20)


# ==========================================
# CREATE DATAFRAME
# ==========================================

profile_df = pd.DataFrame(
    profile_features.numpy(),
    columns=[f"Feature_{i}" for i in range(20)]
)

profile_df["Bot_Label"] = bot_labels.numpy()

# Human-readable class
profile_df["Account_Type"] = profile_df["Bot_Label"].map({
    0: "Human",
    1: "Bot"
})


# ==========================================
# BASIC STATISTICS
# ==========================================

print("\n========== OVERALL STATISTICS ==========")

print(
    profile_df[
        [f"Feature_{i}" for i in range(20)]
    ].describe().round(4)
)


# ==========================================
# HUMAN VS BOT MEANS
# ==========================================

print("\n========== HUMAN VS BOT MEAN ==========")

comparison = profile_df.groupby(
    "Account_Type"
)[
    [f"Feature_{i}" for i in range(20)]
].mean()

print(comparison.round(4).T)


# ==========================================
# HUMAN VS BOT STANDARD DEVIATION
# ==========================================

print("\n========== HUMAN VS BOT STANDARD DEVIATION ==========")

std_comparison = profile_df.groupby(
    "Account_Type"
)[
    [f"Feature_{i}" for i in range(20)]
].std()

print(std_comparison.round(4).T)


# ==========================================
# DIFFERENCE BETWEEN BOT AND HUMAN
# ==========================================

print("\n========== BOT - HUMAN DIFFERENCE ==========")

human_means = comparison.loc["Human"]
bot_means = comparison.loc["Bot"]

difference = bot_means - human_means

difference_df = pd.DataFrame({
    "Human_Mean": human_means,
    "Bot_Mean": bot_means,
    "Difference": difference,
    "Absolute_Difference": difference.abs()
})

difference_df = difference_df.sort_values(
    "Absolute_Difference",
    ascending=False
)

print(difference_df.round(4))


# ==========================================
# TOP 10 DIFFERENT FEATURES
# ==========================================

print("\n========== TOP 10 DIFFERENT FEATURES ==========")

top_features = difference_df.head(10)

print(top_features.round(4))


# ==========================================
# VISUALIZATION
# ==========================================

print("\n========== CREATING PLOTS ==========")

# ------------------------------------------
# Plot 1: Human vs Bot means
# ------------------------------------------

plt.figure(figsize=(12, 6))

x = range(20)

plt.plot(
    x,
    human_means.values,
    marker="o",
    label="Human"
)

plt.plot(
    x,
    bot_means.values,
    marker="o",
    label="Bot"
)

plt.xlabel("Profile Feature")
plt.ylabel("Mean Value")
plt.title("Human vs Bot Profile Feature Means")

plt.xticks(
    range(20),
    [f"F{i}" for i in range(20)]
)

plt.legend()
plt.tight_layout()

plt.savefig(
    "profile_feature_means.png",
    dpi=300
)

plt.show()


# ------------------------------------------
# Plot 2: Top 10 differences
# ------------------------------------------

plt.figure(figsize=(12, 6))

plt.bar(
    top_features.index,
    top_features["Difference"]
)

plt.axhline(
    y=0,
    linestyle="--"
)

plt.xlabel("Profile Feature")
plt.ylabel("Bot Mean - Human Mean")
plt.title("Top 10 Human vs Bot Profile Feature Differences")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "top_profile_feature_differences.png",
    dpi=300
)

plt.show()


print("\n========== EDA COMPLETE ==========")
print("Plots saved:")
print("profile_feature_means.png")
print("top_profile_feature_differences.png")