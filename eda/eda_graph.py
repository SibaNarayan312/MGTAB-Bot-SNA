"""
============================================================
MGTAB GRAPH / NETWORK EDA
============================================================

This script performs Exploratory Data Analysis on the
MGTAB multi-relational graph.

It automatically searches the project for the required
MGTAB .pt files, so the dataset does NOT have to be located
specifically at:

    data/features.pt

Required MGTAB files:

    features.pt
    edge_index.pt
    edge_type.pt
    edge_weight.pt
    labels_stance.pt
    labels_bot.pt

Outputs are saved inside:

    results/graph_eda/

============================================================
"""

import os
import glob
import warnings

import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt

from collections import Counter, defaultdict

warnings.filterwarnings("ignore")


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results",
    "graph_eda"
)

os.makedirs(RESULTS_DIR, exist_ok=True)


# ==========================================================
# RELATION NAMES
# ==========================================================

RELATION_NAMES = {
    0: "Followers",
    1: "Friends",
    2: "Mention",
    3: "Reply",
    4: "Quoted",
    5: "URL",
    6: "Hashtag"
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def print_separator(title=None):

    print("\n" + "=" * 60)

    if title:
        print(title)

    print("=" * 60)


def find_file(filename):
    """
    Search recursively for a specific filename.

    The search begins from the project root.
    """

    matches = glob.glob(
        os.path.join(
            PROJECT_ROOT,
            "**",
            filename
        ),
        recursive=True
    )

    # Avoid files inside Python cache directories
    matches = [
        path for path in matches
        if "__pycache__" not in path
    ]

    if len(matches) == 0:
        return None

    # Prefer Dataset/MGTAB if it exists
    for path in matches:

        normalized = path.replace("\\", "/").lower()

        if "/dataset/mtgab/" in normalized:
            return path

        if "/dataset/mgtab/" in normalized:
            return path

    return matches[0]


def load_tensor(filename, required=True):

    path = find_file(filename)

    if path is None:

        if required:

            raise FileNotFoundError(
                f"\nCould not find:\n"
                f"    {filename}\n\n"
                f"Search location:\n"
                f"    {PROJECT_ROOT}\n\n"
                f"Please check where the MGTAB dataset files "
                f"are stored."
            )

        return None, None

    print(
        f"Loading {filename}: "
        f"{os.path.relpath(path, PROJECT_ROOT)}"
    )

    tensor = torch.load(
        path,
        map_location="cpu",
        weights_only=False
    )

    return tensor, path


def to_numpy(x):

    if torch.is_tensor(x):

        return x.detach().cpu().numpy()

    return np.asarray(x)


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset():

    print_separator("SEARCHING FOR MGTAB DATASET")

    print("Project root:")
    print(PROJECT_ROOT)

    print("\nSearching recursively for MGTAB files...\n")

    features, features_path = load_tensor(
        "features.pt"
    )

    edge_index, edge_index_path = load_tensor(
        "edge_index.pt"
    )

    edge_type, edge_type_path = load_tensor(
        "edge_type.pt"
    )

    edge_weight, edge_weight_path = load_tensor(
        "edge_weight.pt"
    )

    labels_stance, stance_path = load_tensor(
        "labels_stance.pt"
    )

    labels_bot, bot_path = load_tensor(
        "labels_bot.pt"
    )

    print_separator("DATASET FILES FOUND")

    print(
        "Features:",
        os.path.relpath(
            features_path,
            PROJECT_ROOT
        )
    )

    print(
        "Edge index:",
        os.path.relpath(
            edge_index_path,
            PROJECT_ROOT
        )
    )

    print(
        "Edge type:",
        os.path.relpath(
            edge_type_path,
            PROJECT_ROOT
        )
    )

    print(
        "Edge weight:",
        os.path.relpath(
            edge_weight_path,
            PROJECT_ROOT
        )
    )

    print(
        "Stance labels:",
        os.path.relpath(
            stance_path,
            PROJECT_ROOT
        )
    )

    print(
        "Bot labels:",
        os.path.relpath(
            bot_path,
            PROJECT_ROOT
        )
    )

    return (
        features,
        edge_index,
        edge_type,
        edge_weight,
        labels_stance,
        labels_bot
    )


# ==========================================================
# BASIC DATASET INFORMATION
# ==========================================================

def analyze_basic_information(
    features,
    edge_index,
    edge_type,
    edge_weight,
    labels_stance,
    labels_bot
):

    print_separator("GRAPH DATASET INFORMATION")

    # ------------------------------------------------------
    # Features
    # ------------------------------------------------------

    print("Feature shape:", tuple(features.shape))

    if len(features.shape) == 2:

        num_nodes = features.shape[0]
        num_features = features.shape[1]

    else:

        num_nodes = len(features)
        num_features = 0

    # ------------------------------------------------------
    # Edges
    # ------------------------------------------------------

    print(
        "Edge index shape:",
        tuple(edge_index.shape)
    )

    if edge_index.ndim == 2:

        if edge_index.shape[0] == 2:

            num_edges = edge_index.shape[1]

        else:

            num_edges = edge_index.shape[0]

    else:

        num_edges = 0

    print("Number of nodes:", num_nodes)
    print("Number of edges:", num_edges)
    print("Number of features:", num_features)

    # ------------------------------------------------------
    # Labels
    # ------------------------------------------------------

    print(
        "Bot labels:",
        tuple(labels_bot.shape)
    )

    print(
        "Stance labels:",
        tuple(labels_stance.shape)
    )

    # ------------------------------------------------------
    # Graph density
    # ------------------------------------------------------

    if num_nodes > 1:

        possible_edges = (
            num_nodes * (num_nodes - 1)
        )

        density = num_edges / possible_edges

        print(
            f"Directed graph density: "
            f"{density:.8f}"
        )

    # ------------------------------------------------------
    # Average degree
    # ------------------------------------------------------

    if num_nodes > 0:

        avg_degree = (
            num_edges / num_nodes
        )

        print(
            f"Average directed degree: "
            f"{avg_degree:.4f}"
        )

    # ------------------------------------------------------
    # Save summary
    # ------------------------------------------------------

    summary = {

        "Number_of_Nodes": num_nodes,

        "Number_of_Edges": num_edges,

        "Number_of_Features": num_features,

        "Average_Degree": (
            num_edges / num_nodes
            if num_nodes > 0
            else 0
        ),

        "Graph_Density": (
            density
            if num_nodes > 1
            else 0
        )
    }

    pd.DataFrame(
        [summary]
    ).to_csv(
        os.path.join(
            RESULTS_DIR,
            "graph_summary.csv"
        ),
        index=False
    )


# ==========================================================
# BOT LABEL DISTRIBUTION
# ==========================================================

def analyze_bot_labels(labels_bot):

    print_separator("BOT / HUMAN LABEL DISTRIBUTION")

    labels = to_numpy(
        labels_bot
    ).reshape(-1)

    unique, counts = np.unique(
        labels,
        return_counts=True
    )

    total = len(labels)

    rows = []

    for label, count in zip(
        unique,
        counts
    ):

        if int(label) == 0:

            name = "Human"

        elif int(label) == 1:

            name = "Bot"

        else:

            name = f"Class_{label}"

        percentage = (
            count / total * 100
        )

        print(
            f"{name}: "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )

        rows.append(
            {
                "Label": int(label),
                "Account_Type": name,
                "Count": int(count),
                "Percentage": percentage
            }
        )

    df = pd.DataFrame(rows)

    df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "bot_human_distribution.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Plot
    # ------------------------------------------------------

    plt.figure(
        figsize=(7, 5)
    )

    names = [
        row["Account_Type"]
        for row in rows
    ]

    values = [
        row["Count"]
        for row in rows
    ]

    plt.bar(
        names,
        values
    )

    plt.title(
        "Human vs Bot Distribution"
    )

    plt.xlabel(
        "Account Type"
    )

    plt.ylabel(
        "Number of Accounts"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "bot_human_distribution.png"
        ),
        dpi=300
    )

    plt.close()


# ==========================================================
# EDGE TYPE ANALYSIS
# ==========================================================

def analyze_edge_types(
    edge_type,
    edge_index
):

    print_separator(
        "EDGE / RELATION TYPE DISTRIBUTION"
    )

    types = to_numpy(
        edge_type
    ).reshape(-1)

    unique, counts = np.unique(
        types,
        return_counts=True
    )

    total_edges = len(types)

    rows = []

    for relation, count in zip(
        unique,
        counts
    ):

        relation = int(relation)

        name = RELATION_NAMES.get(
            relation,
            f"Relation_{relation}"
        )

        percentage = (
            count /
            total_edges *
            100
        )

        print(
            f"{relation}: "
            f"{name:<12} "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )

        rows.append(
            {
                "Relation_ID": relation,
                "Relation": name,
                "Edge_Count": int(count),
                "Percentage": percentage
            }
        )

    df = pd.DataFrame(rows)

    df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "edge_type_distribution.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Plot
    # ------------------------------------------------------

    plt.figure(
        figsize=(10, 6)
    )

    names = df["Relation"]
    counts = df["Edge_Count"]

    plt.bar(
        names,
        counts
    )

    plt.title(
        "MGTAB Edge Type Distribution"
    )

    plt.xlabel(
        "Relationship Type"
    )

    plt.ylabel(
        "Number of Edges"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "edge_type_distribution.png"
        ),
        dpi=300
    )

    plt.close()


# ==========================================================
# DEGREE ANALYSIS
# ==========================================================

def analyze_degree_distribution(
    edge_index,
    labels_bot
):

    print_separator(
        "NODE DEGREE ANALYSIS"
    )

    edges = to_numpy(
        edge_index
    )

    labels = to_numpy(
        labels_bot
    ).reshape(-1)

    if edges.shape[0] != 2:

        if edges.shape[1] == 2:

            edges = edges.T

        else:

            raise ValueError(
                "edge_index must have shape "
                "[2, num_edges]"
            )

    num_nodes = len(labels)

    sources = edges[0].astype(int)
    targets = edges[1].astype(int)

    # ------------------------------------------------------
    # Filter invalid nodes
    # ------------------------------------------------------

    valid_source = (
        (sources >= 0)
        &
        (sources < num_nodes)
    )

    valid_target = (
        (targets >= 0)
        &
        (targets < num_nodes)
    )

    # ------------------------------------------------------
    # Out-degree
    # ------------------------------------------------------

    out_degree = np.bincount(
        sources[valid_source],
        minlength=num_nodes
    )

    # ------------------------------------------------------
    # In-degree
    # ------------------------------------------------------

    in_degree = np.bincount(
        targets[valid_target],
        minlength=num_nodes
    )

    # ------------------------------------------------------
    # Total degree
    # ------------------------------------------------------

    total_degree = (
        in_degree +
        out_degree
    )

    print(
        f"Average in-degree: "
        f"{np.mean(in_degree):.4f}"
    )

    print(
        f"Average out-degree: "
        f"{np.mean(out_degree):.4f}"
    )

    print(
        f"Average total degree: "
        f"{np.mean(total_degree):.4f}"
    )

    print(
        f"Maximum in-degree: "
        f"{np.max(in_degree):,}"
    )

    print(
        f"Maximum out-degree: "
        f"{np.max(out_degree):,}"
    )

    # ------------------------------------------------------
    # Degree table
    # ------------------------------------------------------

    degree_df = pd.DataFrame(
        {
            "Node": np.arange(
                num_nodes
            ),

            "In_Degree": in_degree,

            "Out_Degree": out_degree,

            "Total_Degree": total_degree,

            "Account_Type": np.where(
                labels == 1,
                "Bot",
                "Human"
            )
        }
    )

    degree_df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "node_degree_statistics.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Top nodes
    # ------------------------------------------------------

    top_nodes = (
        degree_df
        .sort_values(
            "Total_Degree",
            ascending=False
        )
        .head(20)
    )

    print("\nTop 20 highest-degree nodes:")

    print(
        top_nodes[
            [
                "Node",
                "Account_Type",
                "In_Degree",
                "Out_Degree",
                "Total_Degree"
            ]
        ].to_string(
            index=False
        )
    )

    top_nodes.to_csv(
        os.path.join(
            RESULTS_DIR,
            "top_20_high_degree_nodes.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Degree distribution plot
    # ------------------------------------------------------

    plt.figure(
        figsize=(9, 6)
    )

    plt.hist(
        total_degree,
        bins=50
    )

    plt.title(
        "Overall Node Degree Distribution"
    )

    plt.xlabel(
        "Total Degree"
    )

    plt.ylabel(
        "Number of Nodes"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "degree_distribution.png"
        ),
        dpi=300
    )

    plt.close()

    # ------------------------------------------------------
    # Log scale degree distribution
    # ------------------------------------------------------

    positive_degree = (
        total_degree[
            total_degree > 0
        ]
    )

    if len(positive_degree) > 0:

        plt.figure(
            figsize=(9, 6)
        )

        plt.hist(
            positive_degree,
            bins=50
        )

        plt.xscale("log")
        plt.yscale("log")

        plt.title(
            "Degree Distribution (Log-Log Scale)"
        )

        plt.xlabel(
            "Total Degree (log scale)"
        )

        plt.ylabel(
            "Frequency (log scale)"
        )

        plt.tight_layout()

        plt.savefig(
            os.path.join(
                RESULTS_DIR,
                "degree_distribution_loglog.png"
            ),
            dpi=300
        )

        plt.close()

    return (
        in_degree,
        out_degree,
        total_degree
    )


# ==========================================================
# HUMAN VS BOT DEGREE ANALYSIS
# ==========================================================

def analyze_degree_by_account_type(
    in_degree,
    out_degree,
    total_degree,
    labels_bot
):

    print_separator(
        "HUMAN VS BOT DEGREE ANALYSIS"
    )

    labels = to_numpy(
        labels_bot
    ).reshape(-1)

    human_mask = (
        labels == 0
    )

    bot_mask = (
        labels == 1
    )

    groups = {

        "Human": human_mask,

        "Bot": bot_mask
    }

    rows = []

    for name, mask in groups.items():

        if np.sum(mask) == 0:
            continue

        print(
            f"\n{name}"
        )

        print(
            f"Number of nodes: "
            f"{np.sum(mask):,}"
        )

        print(
            f"Average in-degree: "
            f"{np.mean(in_degree[mask]):.4f}"
        )

        print(
            f"Average out-degree: "
            f"{np.mean(out_degree[mask]):.4f}"
        )

        print(
            f"Average total degree: "
            f"{np.mean(total_degree[mask]):.4f}"
        )

        print(
            f"Median total degree: "
            f"{np.median(total_degree[mask]):.4f}"
        )

        rows.append(
            {
                "Account_Type": name,

                "Node_Count": int(
                    np.sum(mask)
                ),

                "Average_In_Degree":
                    np.mean(
                        in_degree[mask]
                    ),

                "Average_Out_Degree":
                    np.mean(
                        out_degree[mask]
                    ),

                "Average_Total_Degree":
                    np.mean(
                        total_degree[mask]
                    ),

                "Median_Total_Degree":
                    np.median(
                        total_degree[mask]
                    )
            }
        )

    df = pd.DataFrame(rows)

    df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "human_vs_bot_degree.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Boxplot
    # ------------------------------------------------------

    human_degree = (
        total_degree[human_mask]
    )

    bot_degree = (
        total_degree[bot_mask]
    )

    plt.figure(
        figsize=(8, 6)
    )

    plt.boxplot(
        [
            human_degree,
            bot_degree
        ],
        tick_labels=[
            "Human",
            "Bot"
        ],
        showfliers=False
    )

    plt.title(
        "Human vs Bot Degree Distribution"
    )

    plt.xlabel(
        "Account Type"
    )

    plt.ylabel(
        "Total Degree"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "human_vs_bot_degree_boxplot.png"
        ),
        dpi=300
    )

    plt.close()


# ==========================================================
# DEGREE BY RELATION TYPE
# ==========================================================

def analyze_relation_degree(
    edge_index,
    edge_type,
    labels_bot
):

    print_separator(
        "RELATION-SPECIFIC DEGREE ANALYSIS"
    )

    edges = to_numpy(
        edge_index
    )

    types = to_numpy(
        edge_type
    ).reshape(-1)

    labels = to_numpy(
        labels_bot
    ).reshape(-1)

    if edges.shape[0] != 2:

        edges = edges.T

    sources = edges[0].astype(int)

    targets = edges[1].astype(int)

    num_nodes = len(labels)

    rows = []

    for relation in sorted(
        np.unique(types)
    ):

        relation = int(relation)

        name = RELATION_NAMES.get(
            relation,
            f"Relation_{relation}"
        )

        mask = (
            types == relation
        )

        relation_sources = (
            sources[mask]
        )

        relation_targets = (
            targets[mask]
        )

        valid_s = (
            (relation_sources >= 0)
            &
            (relation_sources < num_nodes)
        )

        valid_t = (
            (relation_targets >= 0)
            &
            (relation_targets < num_nodes)
        )

        out_degree = np.bincount(
            relation_sources[valid_s],
            minlength=num_nodes
        )

        in_degree = np.bincount(
            relation_targets[valid_t],
            minlength=num_nodes
        )

        total_degree = (
            in_degree +
            out_degree
        )

        human_mask = (
            labels == 0
        )

        bot_mask = (
            labels == 1
        )

        rows.append(
            {
                "Relation_ID": relation,

                "Relation": name,

                "Total_Edges":
                    int(np.sum(mask)),

                "Human_Average_Degree":
                    float(
                        np.mean(
                            total_degree[
                                human_mask
                            ]
                        )
                    ),

                "Bot_Average_Degree":
                    float(
                        np.mean(
                            total_degree[
                                bot_mask
                            ]
                        )
                    ),

                "Overall_Average_Degree":
                    float(
                        np.mean(
                            total_degree
                        )
                    )
            }
        )

    df = pd.DataFrame(rows)

    print(
        df.to_string(
            index=False
        )
    )

    df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "relation_specific_degree.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Plot
    # ------------------------------------------------------

    x = np.arange(
        len(df)
    )

    width = 0.35

    plt.figure(
        figsize=(11, 6)
    )

    plt.bar(
        x - width / 2,
        df["Human_Average_Degree"],
        width,
        label="Human"
    )

    plt.bar(
        x + width / 2,
        df["Bot_Average_Degree"],
        width,
        label="Bot"
    )

    plt.xticks(
        x,
        df["Relation"],
        rotation=30,
        ha="right"
    )

    plt.xlabel(
        "Relationship Type"
    )

    plt.ylabel(
        "Average Degree"
    )

    plt.title(
        "Human vs Bot Degree by Relationship Type"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "relation_degree_human_vs_bot.png"
        ),
        dpi=300
    )

    plt.close()


# ==========================================================
# SELF LOOP ANALYSIS
# ==========================================================

def analyze_self_loops(edge_index):

    print_separator(
        "SELF-LOOP ANALYSIS"
    )

    edges = to_numpy(
        edge_index
    )

    if edges.shape[0] != 2:

        edges = edges.T

    sources = edges[0]
    targets = edges[1]

    self_loops = (
        sources == targets
    )

    count = int(
        np.sum(self_loops)
    )

    total = len(sources)

    percentage = (
        count / total * 100
        if total > 0
        else 0
    )

    print(
        f"Self-loops: "
        f"{count:,}"
    )

    print(
        f"Percentage: "
        f"{percentage:.6f}%"
    )

    pd.DataFrame(
        [
            {
                "Self_Loops": count,
                "Percentage": percentage
            }
        ]
    ).to_csv(
        os.path.join(
            RESULTS_DIR,
            "self_loop_statistics.csv"
        ),
        index=False
    )


# ==========================================================
# DUPLICATE EDGE ANALYSIS
# ==========================================================

def analyze_duplicate_edges(
    edge_index
):

    print_separator(
        "DUPLICATE EDGE ANALYSIS"
    )

    edges = to_numpy(
        edge_index
    )

    if edges.shape[0] != 2:

        edges = edges.T

    edge_pairs = list(
        zip(
            edges[0].astype(int),
            edges[1].astype(int)
        )
    )

    total_edges = len(
        edge_pairs
    )

    unique_edges = len(
        set(edge_pairs)
    )

    duplicate_edges = (
        total_edges -
        unique_edges
    )

    percentage = (
        duplicate_edges /
        total_edges *
        100
        if total_edges > 0
        else 0
    )

    print(
        f"Total edges: "
        f"{total_edges:,}"
    )

    print(
        f"Unique edges: "
        f"{unique_edges:,}"
    )

    print(
        f"Duplicate edges: "
        f"{duplicate_edges:,}"
    )

    print(
        f"Duplicate percentage: "
        f"{percentage:.4f}%"
    )

    pd.DataFrame(
        [
            {
                "Total_Edges":
                    total_edges,

                "Unique_Edges":
                    unique_edges,

                "Duplicate_Edges":
                    duplicate_edges,

                "Duplicate_Percentage":
                    percentage
            }
        ]
    ).to_csv(
        os.path.join(
            RESULTS_DIR,
            "duplicate_edge_statistics.csv"
        ),
        index=False
    )


# ==========================================================
# RECIPROCAL EDGE ANALYSIS
# ==========================================================

def analyze_reciprocal_edges(
    edge_index
):

    print_separator(
        "RECIPROCAL EDGE ANALYSIS"
    )

    edges = to_numpy(
        edge_index
    )

    if edges.shape[0] != 2:

        edges = edges.T

    sources = edges[0].astype(int)
    targets = edges[1].astype(int)

    edge_set = set(
        zip(
            sources,
            targets
        )
    )

    reciprocal_count = 0

    checked = set()

    for source, target in edge_set:

        if source == target:
            continue

        pair = tuple(
            sorted(
                [source, target]
            )
        )

        if pair in checked:
            continue

        checked.add(pair)

        if (
            (source, target)
            in edge_set
            and
            (target, source)
            in edge_set
        ):

            reciprocal_count += 1

    total_unique_edges = len(
        edge_set
    )

    percentage = (
        reciprocal_count /
        total_unique_edges *
        100
        if total_unique_edges > 0
        else 0
    )

    print(
        f"Reciprocal edge pairs: "
        f"{reciprocal_count:,}"
    )

    print(
        f"Percentage of unique edges "
        f"in reciprocal relationships: "
        f"{percentage:.4f}%"
    )

    pd.DataFrame(
        [
            {
                "Reciprocal_Pairs":
                    reciprocal_count,

                "Percentage":
                    percentage
            }
        ]
    ).to_csv(
        os.path.join(
            RESULTS_DIR,
            "reciprocal_edge_statistics.csv"
        ),
        index=False
    )


# ==========================================================
# FEATURE VS DEGREE CORRELATION
# ==========================================================

def analyze_feature_degree_relationship(
    features,
    total_degree
):

    print_separator(
        "FEATURE VS GRAPH DEGREE ANALYSIS"
    )

    x = to_numpy(
        features
    ).astype(
        np.float64
    )

    degrees = (
        total_degree.astype(
            np.float64
        )
    )

    # ------------------------------------------------------
    # Make sure node counts match
    # ------------------------------------------------------

    n = min(
        x.shape[0],
        len(degrees)
    )

    x = x[:n]
    degrees = degrees[:n]

    # ------------------------------------------------------
    # Correlation
    # ------------------------------------------------------

    correlations = []

    for i in range(
        x.shape[1]
    ):

        feature = x[:, i]

        if (
            np.std(feature) == 0
            or
            np.std(degrees) == 0
        ):

            correlation = 0

        else:

            correlation = np.corrcoef(
                feature,
                degrees
            )[0, 1]

        correlations.append(
            correlation
        )

    corr_df = pd.DataFrame(
        {
            "Feature":
                [
                    f"Feature_{i+1}"
                    for i in range(
                        len(correlations)
                    )
                ],

            "Degree_Correlation":
                correlations,

            "Absolute_Correlation":
                np.abs(
                    correlations
                )
        }
    )

    corr_df = (
        corr_df
        .sort_values(
            "Absolute_Correlation",
            ascending=False
        )
    )

    print(
        "\nTop 20 features correlated "
        "with total degree:"
    )

    print(
        corr_df.head(20).to_string(
            index=False
        )
    )

    corr_df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "feature_degree_correlations.csv"
        ),
        index=False
    )

    # ------------------------------------------------------
    # Top 10 plot
    # ------------------------------------------------------

    top = corr_df.head(10)

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        top["Feature"],
        top["Degree_Correlation"]
    )

    plt.axhline(
        0,
        linestyle="--"
    )

    plt.title(
        "Top 10 Feature-Degree Correlations"
    )

    plt.xlabel(
        "Feature"
    )

    plt.ylabel(
        "Correlation"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "top_feature_degree_correlations.png"
        ),
        dpi=300
    )

    plt.close()


# ==========================================================
# GRAPH STATISTICS TEXT REPORT
# ==========================================================

def create_report(
    features,
    edge_index,
    edge_type,
    labels_bot,
    in_degree,
    out_degree,
    total_degree
):

    print_separator(
        "CREATING GRAPH EDA REPORT"
    )

    num_nodes = (
        features.shape[0]
    )

    num_features = (
        features.shape[1]
    )

    num_edges = (
        edge_index.shape[1]
        if edge_index.shape[0] == 2
        else edge_index.shape[0]
    )

    labels = to_numpy(
        labels_bot
    ).reshape(-1)

    human_count = int(
        np.sum(labels == 0)
    )

    bot_count = int(
        np.sum(labels == 1)
    )

    relation_count = len(
        np.unique(
            to_numpy(edge_type)
        )
    )

    report_path = os.path.join(
        RESULTS_DIR,
        "graph_eda_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "MGTAB GRAPH / NETWORK EDA REPORT\n"
        )

        f.write(
            "=" * 60 + "\n\n"
        )

        f.write(
            f"Number of nodes: "
            f"{num_nodes:,}\n"
        )

        f.write(
            f"Number of edges: "
            f"{num_edges:,}\n"
        )

        f.write(
            f"Number of features: "
            f"{num_features:,}\n"
        )

        f.write(
            f"Number of relationship types: "
            f"{relation_count}\n\n"
        )

        f.write(
            f"Human accounts: "
            f"{human_count:,}\n"
        )

        f.write(
            f"Bot accounts: "
            f"{bot_count:,}\n\n"
        )

        f.write(
            f"Average in-degree: "
            f"{np.mean(in_degree):.4f}\n"
        )

        f.write(
            f"Average out-degree: "
            f"{np.mean(out_degree):.4f}\n"
        )

        f.write(
            f"Average total degree: "
            f"{np.mean(total_degree):.4f}\n"
        )

        f.write(
            f"Median total degree: "
            f"{np.median(total_degree):.4f}\n"
        )

        f.write(
            f"Maximum total degree: "
            f"{np.max(total_degree):,}\n"
        )

    print(
        "Saved:",
        report_path
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print_separator(
        "MGTAB GRAPH / NETWORK EDA"
    )

    print(
        "This analysis automatically searches "
        "for the MGTAB dataset files."
    )

    print(
        "\nResults directory:"
    )

    print(
        RESULTS_DIR
    )

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    (
        features,
        edge_index,
        edge_type,
        edge_weight,
        labels_stance,
        labels_bot
    ) = load_dataset()

    # ------------------------------------------------------
    # Convert data types
    # ------------------------------------------------------

    if not torch.is_tensor(features):

        features = torch.tensor(
            features
        )

    if not torch.is_tensor(edge_index):

        edge_index = torch.tensor(
            edge_index
        )

    if not torch.is_tensor(edge_type):

        edge_type = torch.tensor(
            edge_type
        )

    if not torch.is_tensor(edge_weight):

        edge_weight = torch.tensor(
            edge_weight
        )

    if not torch.is_tensor(labels_bot):

        labels_bot = torch.tensor(
            labels_bot
        )

    if not torch.is_tensor(labels_stance):

        labels_stance = torch.tensor(
            labels_stance
        )

    # ------------------------------------------------------
    # Make sure edge_index is [2, E]
    # ------------------------------------------------------

    if (
        edge_index.ndim == 2
        and
        edge_index.shape[0] != 2
        and
        edge_index.shape[1] == 2
    ):

        edge_index = edge_index.T

    # ------------------------------------------------------
    # Print tensor information
    # ------------------------------------------------------

    print_separator(
        "LOADED DATA SHAPES"
    )

    print(
        "Features:",
        tuple(features.shape)
    )

    print(
        "Edge index:",
        tuple(edge_index.shape)
    )

    print(
        "Edge type:",
        tuple(edge_type.shape)
    )

    print(
        "Edge weight:",
        tuple(edge_weight.shape)
    )

    print(
        "Stance labels:",
        tuple(labels_stance.shape)
    )

    print(
        "Bot labels:",
        tuple(labels_bot.shape)
    )

    # ------------------------------------------------------
    # BASIC INFORMATION
    # ------------------------------------------------------

    analyze_basic_information(
        features,
        edge_index,
        edge_type,
        edge_weight,
        labels_stance,
        labels_bot
    )

    # ------------------------------------------------------
    # BOT / HUMAN DISTRIBUTION
    # ------------------------------------------------------

    analyze_bot_labels(
        labels_bot
    )

    # ------------------------------------------------------
    # EDGE TYPES
    # ------------------------------------------------------

    analyze_edge_types(
        edge_type,
        edge_index
    )

    # ------------------------------------------------------
    # DEGREE
    # ------------------------------------------------------

    (
        in_degree,
        out_degree,
        total_degree
    ) = analyze_degree_distribution(
        edge_index,
        labels_bot
    )

    # ------------------------------------------------------
    # HUMAN VS BOT DEGREE
    # ------------------------------------------------------

    analyze_degree_by_account_type(
        in_degree,
        out_degree,
        total_degree,
        labels_bot
    )

    # ------------------------------------------------------
    # RELATION-SPECIFIC DEGREE
    # ------------------------------------------------------

    analyze_relation_degree(
        edge_index,
        edge_type,
        labels_bot
    )

    # ------------------------------------------------------
    # SELF LOOPS
    # ------------------------------------------------------

    analyze_self_loops(
        edge_index
    )

    # ------------------------------------------------------
    # DUPLICATE EDGES
    # ------------------------------------------------------

    analyze_duplicate_edges(
        edge_index
    )

    # ------------------------------------------------------
    # RECIPROCAL EDGES
    # ------------------------------------------------------

    analyze_reciprocal_edges(
        edge_index
    )

    # ------------------------------------------------------
    # FEATURE / DEGREE RELATIONSHIP
    # ------------------------------------------------------

    analyze_feature_degree_relationship(
        features,
        total_degree
    )

    # ------------------------------------------------------
    # REPORT
    # ------------------------------------------------------

    create_report(
        features,
        edge_index,
        edge_type,
        labels_bot,
        in_degree,
        out_degree,
        total_degree
    )

    # ------------------------------------------------------
    # COMPLETE
    # ------------------------------------------------------

    print_separator(
        "GRAPH EDA COMPLETE"
    )

    print(
        "\nAll results have been saved to:"
    )

    print(
        RESULTS_DIR
    )

    print("\nGenerated files include:")

    for filename in sorted(
        os.listdir(
            RESULTS_DIR
        )
    ):

        print(
            " -",
            filename
        )

    print(
        "\n============================================================"
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()