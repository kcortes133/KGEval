"""
mappingstest.py
===============

Schema-coverage heatmaps for biomedical knowledge graphs (KGs)
(manuscript Figures 3B and 4B).

Each surveyed KG declares its own edge types and node types. To compare
them on a common semantic backbone, every native label is mapped onto a
Biolink Model 4.4.5 term by ``map_biolink.py`` (run it first).

Inputs
------
* ``inputs/Edge Types.csv``  - KG x native-edge-type presence matrix.
* ``inputs/Node Types.csv``  - KG x native-node-type presence matrix.
* ``outputs/edge_type_biolink_mapping.csv`` / ``node_type_biolink_mapping.csv``
  - validated native label -> Biolink mapping from ``map_biolink.py``.

Outputs
-------
* ``outputs/kg_node_type_counts.csv``, ``outputs/kg_edge_type_counts.csv``
  - native node / edge types per KG (Figures 3A, 4A).
* ``outputs/kg_biolink_{node,edge,combined}_matrix.csv`` - Biolink term x KG
  counts of native labels.
* ``figures/kg_biolink_{node,edge,schema}_heatmap.svg`` - clustered heatmaps.
  Columns (KGs) are clustered by Ward linkage; rows stay alphabetical.

Reference
---------
Cortes et al., "Improving Biomedical Knowledge Graph Transparency and
Reusability: A Community Approach." Preprint: arXiv:2508.21774 (2025).
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
    plt.close("all")

# -----------------------------
# Biolink-level matrices and heatmaps
# -----------------------------
# The native -> Biolink mapping is produced (and validated against Biolink
# 4.4.5) by ``map_biolink.py``; run that first. Labels with no Biolink term
# ("unresolved") or that are internal metadata ("no_biolink_equivalent") are
# left out of the Biolink-level matrices.
OUT, FIG = "../outputs", "../figures"


def biolink_matrix(type_file, map_file):
    native, kgs = load_presence_matrix(type_file)
    mapping = pd.read_csv(map_file, usecols=["original", "biolink_mapping"])
    mapping.columns = ["original", "biolink"]
    mapping["original"] = mapping["original"].str.strip()
    mapped = native.merge(mapping, on="original", how="left")
    mapped = mapped[mapped["biolink"].fillna("").str.startswith("biolink:")]
    # Per (Biolink term, KG): number of native labels in that KG mapping to
    # the term. Sum (not clip) keeps multi-mapping intensity.
    return native, kgs, mapped.groupby("biolink")[kgs].sum().sort_index()


edge_native, kg_columns, edge_biolink = biolink_matrix(
    "../inputs/Edge Types.csv", f"{OUT}/edge_type_biolink_mapping.csv")
node_native, _, node_biolink = biolink_matrix(
    "../inputs/Node Types.csv", f"{OUT}/node_type_biolink_mapping.csv")

# Native type counts per KG (Figures 3A and 4A).
pd.DataFrame({"KG": kg_columns, "node_types": node_native[kg_columns].sum().values}) \
    .to_csv(f"{OUT}/kg_node_type_counts.csv", index=False)
pd.DataFrame({"KG": kg_columns, "edge_types": edge_native[kg_columns].sum().values}) \
    .to_csv(f"{OUT}/kg_edge_type_counts.csv", index=False)

edge_biolink.to_csv(f"{OUT}/kg_biolink_edge_matrix.csv")
node_biolink.to_csv(f"{OUT}/kg_biolink_node_matrix.csv")
combined = pd.concat([node_biolink, edge_biolink])
combined.to_csv(f"{OUT}/kg_biolink_combined_matrix.csv")

# KGs with no mapped labels (e.g. EmBiology, whose schema is paywalled) have
# all-zero columns, which Ward linkage cannot cluster; leave them out.
def nonzero(m):
    # Also drop the CURIE prefix from row labels for readability.
    return m.loc[:, m.sum() > 0].rename(index=lambda s: s.replace("biolink:", ""))

plot_heatmap(nonzero(edge_biolink), out_svg=f"{FIG}/kg_biolink_edge_heatmap.svg",
             ylabel="Biolink Edge Type")
plot_heatmap(nonzero(node_biolink), out_svg=f"{FIG}/kg_biolink_node_heatmap.svg",
             ylabel="Biolink Node Class")
plot_heatmap(nonzero(combined), out_svg=f"{FIG}/kg_biolink_schema_heatmap.svg",
             ylabel="Biolink Node Class / Edge Type")
