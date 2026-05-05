"""
mappingstest.py
===============

Schema-coverage heatmaps for biomedical knowledge graphs (KGs).

Each surveyed KG declares its own edge types and node types. To compare
them on a common semantic backbone we map every native edge / node label
onto a *Biolink Model* term (https://biolink.github.io/biolink-model/)
using the mapping tables ``biolink_edge_mappings.csv`` and
``biolink_node_mappings.csv``.

This script produces two clustered heatmaps:

    1. KG x Biolink **edge type**  coverage -> ``kg_biolink_edge_heatmap.svg``
    2. KG x Biolink **node class** coverage -> ``kg_biolink_node_heatmap.svg``

Columns (KGs) are clustered by Ward linkage so that KGs with similar
schema coverage appear next to each other; rows (Biolink terms) keep
their alphabetical order to make the heatmap easy to read.

Inputs
------
* ``Edge Types.csv``               - KG x native-edge-type presence matrix.
* ``Node Types.csv``               - KG x native-node-type presence matrix.
* ``biolink_edge_mappings.csv``    - native edge type -> Biolink predicate.
* ``biolink_node_mappings.csv``    - native node type -> Biolink class.

Reference
---------
Cortes et al., "Improving Biomedical Knowledge Graph Quality: A Community
Approach," arXiv:2508.21774 (2025).
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage

# -----------------------------
# Shared helpers
# -----------------------------
def load_presence_matrix(file):
    """Load a KG x label TRUE/FALSE matrix and convert to 0/1 ints.

    The first column of the CSV holds the native (original) label - either
    a native edge type or a native node type, depending on the file.
    Every remaining column is one KG.

    Parameters
    ----------
    file : str
        Path to the presence/absence CSV.

    Returns
    -------
    (pandas.DataFrame, pandas.Index)
        The cleaned dataframe with an "original" label column followed
        by one int (0/1) column per KG, plus the Index of KG column
        names.
    """
    df = pd.read_csv(file)
    # First column holds the native label - rename for readability.
    df = df.rename(columns={df.columns[0]: "original"})
    kg_cols = df.columns[1:]
    # Convert TRUE/FALSE strings into 0/1 so we can sum / cluster.
    df[kg_cols] = df[kg_cols].replace(
        {"TRUE": 1, "FALSE": 0}
    ).astype(int)
    # Whitespace in source CSVs is common; strip it so the merge against
    # the Biolink mapping tables joins cleanly.
    df["original"] = df["original"].str.strip()
    return df, kg_cols

def plot_heatmap(matrix, out_svg, ylabel):
    """Render a clustered KG x Biolink-term heatmap and save it as SVG.

    Columns (KGs) are clustered with Ward linkage on the *transposed*
    matrix, i.e. KGs with similar Biolink-coverage profiles end up
    adjacent. Rows (Biolink terms) are *not* clustered - they are kept
    in the alphabetical order set by the caller, which makes the figure
    easier to read alongside the Biolink Model documentation.

    Parameters
    ----------
    matrix : pandas.DataFrame
        Rows = Biolink terms, columns = KGs, values = number of native
        labels in that KG that map to the Biolink term.
    out_svg : str
        Output filename for the SVG figure.
    ylabel : str
        (Currently unused; row/column axis labels are commented out
        below to keep the published figures uncluttered.)
    """
    # Hierarchical clustering of KGs on their Biolink-coverage vectors.
    kg_linkage = linkage(matrix.T, method="ward")

    g = sns.clustermap(
        matrix,
        col_linkage=kg_linkage,
        row_cluster=False,        # Keep Biolink terms in alphabetical order.
        cmap="crest",
        linewidths=0.5,
        linecolor="black",
        figsize=(14, 14),
        dendrogram_ratio=0.05,
        cbar_pos=None             # No colorbar - figure used in publication.
    )

    # Axis labels intentionally omitted from the saved figure.
    #g.ax_heatmap.set_xlabel("Knowledge Graph")
    #g.ax_heatmap.set_ylabel(ylabel)

    # Rotate KG names vertically so long names don't overlap.
    plt.setp(
        g.ax_heatmap.get_xticklabels(),
        rotation=90,
        ha="center",
        va="top",
        fontsize=20
    )

    g.ax_heatmap.tick_params(axis="y", labelsize=16)

    plt.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.show()

# -----------------------------
# EDGE TYPE HEATMAP
# -----------------------------
# Native edge-type presence matrix (rows = native edge labels, cols = KGs).
EDGE_TYPE_FILE = "../data/Edge Types.csv"
# Lookup table mapping each native edge label onto a Biolink predicate.
EDGE_MAP_FILE = "../data/biolink_edge_mappings.csv"

edge_df, kg_columns = load_presence_matrix(EDGE_TYPE_FILE)

# Load and tidy the native -> Biolink edge mapping.
edge_map = pd.read_csv(EDGE_MAP_FILE)
edge_map.columns = ["original", "biolink"]
edge_map["original"] = edge_map["original"].str.strip()

# Attach the Biolink predicate to each row of the native presence matrix.
# Rows that have no Biolink mapping are dropped from the figure.
edge_mapped = (
    edge_df
    .merge(edge_map, on="original", how="left")
    .dropna(subset=["biolink"])
)

# Aggregate to the Biolink level: per (Biolink predicate, KG), count how
# many native edge labels in that KG map to the predicate. Sum (rather
# than .clip(upper=1)) preserves multi-mapping intensity.
edge_biolink = (
    edge_mapped
    .groupby("biolink")[kg_columns]
    .sum()
    #.clip(upper=1)
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
# Native node-type presence matrix.
NODE_TYPE_FILE = "../data/Node Types.csv"
# Lookup table mapping each native node label onto a Biolink class.
NODE_MAP_FILE = "../data/biolink_node_mappings.csv"

node_df, _ = load_presence_matrix(NODE_TYPE_FILE)

# The node mapping CSV has more columns than we need - keep just the
# native label and the Biolink class.
node_map = pd.read_csv(NODE_MAP_FILE)[
    ["Unstructured Label (Node-Type)", "Biolink Class"]
]
node_map.columns = ["original", "biolink"]
node_map["original"] = node_map["original"].str.strip()

# Same join + drop-unmapped pattern as the edge pipeline above.
node_mapped = (
    node_df
    .merge(node_map, on="original", how="left")
    .dropna(subset=["biolink"])
)

# Aggregate native node labels up to Biolink classes.
node_biolink = (
    node_mapped
    .groupby("biolink")[kg_columns]
    .sum()
    #.clip(upper=1)
    .sort_index()
)

plot_heatmap(
    node_biolink,
    out_svg="kg_biolink_node_heatmap.svg",
    ylabel="Biolink Node Class"
)
