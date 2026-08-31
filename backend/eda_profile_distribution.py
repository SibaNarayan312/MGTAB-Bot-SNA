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

# First 20 features = profile features
profile_features = features[:, :20]

feature_names = [
    f"Feature_{i}" for i in range(20)
]

# Convert to DataFrame
df = pd.DataFrame(
    profile_features.numpy(),
    columns=feature_names
)

df["Bot_Label"] = bot_labels.numpy()

df["Account_Type"] = df["Bot_Label"].map({
    0: "Human",
    1: "Bot"
})


# ==========================================
# TOP FEATURES FROM PREVIOUS EDA
# ==========================================

top_features = [
    "Feature_18",
    "Feature_13",
    "Feature_1",
    "Feature_17",
    "Feature_16",
    "Feature_8",
    "Feature_19",
    "Feature_15",
    "Feature_4",
    "Feature_3"
]


# ==========================================
# PRINT MEDIAN VALUES
# ==========================================

print("========== DISTRIBUTION ANALYSIS ==========")

print("\nMedian values: Human vs Bot")

median_values = df.groupby(
    "Account_Type"
)[top_features].median()

print(median_values.round(4).T)


# ==========================================
# PRINT QUARTILES
# ==========================================

print("\n========== QUARTILES ==========")

for feature in top_features:

    human_data = df[
        df["Account_Type"] == "Human"
    ][feature]

    bot_data = df[
        df["Account_Type"] == "Bot"
    ][feature]

    print(f"\n{feature}")

    print(
        "Human Q1:",
        round(human_data.quantile(0.25), 4),
        "| Median:",
        round(human_data.median(), 4),
        "| Q3:",
        round(human_data.quantile(0.75), 4)
    )

    print(
        "Bot   Q1:",
        round(bot_data.quantile(0.25), 4),
        "| Median:",
        round(bot_data.median(), 4),
        "| Q3:",
        round(bot_data.quantile(0.75), 4)
    )


# ==========================================
# CREATE BOXPLOTS
# ==========================================

print("\n========== CREATING BOXPLOTS ==========")

for feature in top_features:

    human_data = df[
        df["Account_Type"] == "Human"
    ][feature]

    bot_data = df[
        df["Account_Type"] == "Bot"
    ][feature]

    plt.figure(figsize=(7, 5))

    plt.boxplot(
        [human_data, bot_data],
        labels=["Human", "Bot"]
    )

    plt.title(
        f"{feature}: Human vs Bot"
    )

    plt.xlabel("Account Type")
    plt.ylabel("Feature Value")

    plt.tight_layout()

    filename = (
        f"{feature.lower()}_human_vs_bot.png"
    )

    plt.savefig(
        filename,
        dpi=300
    )

    plt.show()


print("\n========== DISTRIBUTION ANALYSIS COMPLETE ==========")

print("Created boxplots for:")
for feature in top_features:
    print("-", feature)