import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage

# -----------------------------
# Shared helpers
# -----------------------------
def load_presence_matrix(file):
    df = pd.read_csv(file)
    df = df.rename(columns={df.columns[0]: "original"})
    kg_cols = df.columns[1:]
    df[kg_cols] = df[kg_cols].replace(
        {"TRUE": 1, "FALSE": 0}
    ).astype(int)
    df["original"] = df["original"].str.strip()
    return df, kg_cols

def plot_heatmap(matrix, out_svg, ylabel):
    kg_linkage = linkage(matrix.T, method="ward")

    g = sns.clustermap(
        matrix,
        col_linkage=kg_linkage,
        row_cluster=False,
        cmap="crest",
        linewidths=0.5,
        linecolor="black",
        figsize=(16, 16),
        cbar_pos=(0.02, 0.8, 0.02, 0.18)
    )

    g.ax_heatmap.set_xlabel("Knowledge Graph")
    g.ax_heatmap.set_ylabel(ylabel)

    plt.setp(
        g.ax_heatmap.get_xticklabels(),
        rotation=90,
        ha="center",
        va="top"
    )

    g.ax_heatmap.tick_params(axis="y", labelsize=9)

    plt.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.show()

# -----------------------------
# EDGE TYPE HEATMAP
# -----------------------------
EDGE_TYPE_FILE = "Edge Types.csv"
EDGE_MAP_FILE = "biolink_edge_mappings.csv"

edge_df, kg_columns = load_presence_matrix(EDGE_TYPE_FILE)

edge_map = pd.read_csv(EDGE_MAP_FILE)
edge_map.columns = ["original", "biolink"]
edge_map["original"] = edge_map["original"].str.strip()

edge_mapped = (
    edge_df
    .merge(edge_map, on="original", how="left")
    .dropna(subset=["biolink"])
)

edge_biolink = (
    edge_mapped
    .groupby("biolink")[kg_columns]
    .sum()
    .clip(upper=1)
    .sort_index()
)

plot_heatmap(
    edge_biolink,
    out_svg="kg_biolink_edge_heatmap.svg",
    ylabel="Biolink Edge Type"
)

# -----------------------------
# NODE TYPE HEATMAP
# -----------------------------
NODE_TYPE_FILE = "Node Types.csv"
NODE_MAP_FILE = "biolink_node_mappings.csv"

node_df, _ = load_presence_matrix(NODE_TYPE_FILE)

node_map = pd.read_csv(NODE_MAP_FILE)[
    ["Unstructured Label (Node-Type)", "Biolink Class"]
]
node_map.columns = ["original", "biolink"]
node_map["original"] = node_map["original"].str.strip()

node_mapped = (
    node_df
    .merge(node_map, on="original", how="left")
    .dropna(subset=["biolink"])
)

node_biolink = (
    node_mapped
    .groupby("biolink")[kg_columns]
    .sum()
    .clip(upper=1)
    .sort_index()
)

plot_heatmap(
    node_biolink,
    out_svg="kg_biolink_node_heatmap.svg",
    ylabel="Biolink Node Class"
)
