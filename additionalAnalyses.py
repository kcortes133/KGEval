"""
additionalAnalyses.py
=====================

Cross-KG quantitative analyses that build on top of the per-KG source
counts written by ``sources.py`` and the Biolink edge-coverage matrix
written by ``mappingstest.py``.

The script computes three derived metrics for every KG:

    * ``ontology_ratio``        = ontology_sources / total_sources
    * ``biolink_edge_coverage`` = number of Biolink predicates the KG
                                  covers (column sum of the Biolink edge
                                  matrix)
    * ``edge_type_entropy``     = Shannon entropy (base 2) of the
                                  Biolink-edge distribution within the KG

It then produces two multi-panel SVG figures:

    1. ``kg_source_semantics_multifigure.svg`` (1 x 3 panels)
        A. Ontology reliance vs Biolink edge coverage   (scatter)
        B. Source diversity vs edge-type entropy         (scatter)
        C. KG clustering by source composition           (Ward dendrogram)

    2. ``kg_source_semantics_full.svg`` (2 x 3 panels) - extended version
        A, B, C as above
        D. Edge-type rarefaction curves
        E. Ontology vs non-ontology subgraph coverage    (approximate)
        F. Placeholder for a node-type alignment panel

The second pass also prints two Spearman correlations to stdout:

    rho(ontology_ratio,  biolink_edge_coverage)
    rho(total_sources,    edge_type_entropy)

NOTE: this file deliberately runs the analysis twice (once with three
panels, once with six). Both figures are referenced in the manuscript /
supplement.

Reference
---------
Cortes et al., "Improving Biomedical Knowledge Graph Quality: A Community
Approach," arXiv:2508.21774 (2025).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import entropy
from scipy.cluster.hierarchy import linkage, dendrogram

# =============================================================================
# Pass 1: 3-panel figure (Panels A, B, C) -> kg_source_semantics_multifigure.svg
# =============================================================================

# -----------------------------
# Load data
# -----------------------------
# Per-KG source counts produced by ``sources.py``.
kg_sources = pd.read_csv("kg_source_counts.csv")
# Biolink edge-coverage matrix (rows = Biolink predicates, columns = KGs).
biolink_edges = pd.read_csv(
    "kg_biolink_edge_matrix.csv",
    index_col=0
)

# -----------------------------
# Metrics
# -----------------------------
# Fraction of each KG's sources that are formal ontologies.
kg_sources["ontology_ratio"] = (
    kg_sources["ontology_sources"] /
    kg_sources["total_sources"]
)

# Total weight per KG across all Biolink edge types - used as a proxy for
# how broadly the KG covers the Biolink predicate space.
biolink_coverage = biolink_edges.sum(axis=0)
kg_sources["biolink_edge_coverage"] = (
    kg_sources["KG"].map(biolink_coverage)
)

# Shannon entropy of the per-KG Biolink edge-type distribution. Higher
# entropy => more even spread across predicates; lower => a few predicates
# dominate the schema.
edge_entropy = {}
for kg in biolink_edges.columns:
    vals = biolink_edges[kg].values
    if vals.sum() == 0:
        edge_entropy[kg] = 0
    else:
        p = vals / vals.sum()
        edge_entropy[kg] = entropy(p, base=2)

kg_sources["edge_type_entropy"] = (
    kg_sources["KG"].map(edge_entropy)
)

# -----------------------------
# Figure layout (1 row x 3 cols)
# -----------------------------
sns.set(style="white")
fig = plt.figure(figsize=(14, 6))

# ===== Panel A: ontology reliance vs Biolink edge coverage =====
# Each point is a KG. X = how ontology-heavy its source mix is, Y = how
# many Biolink edge types it covers.
ax1 = fig.add_subplot(1, 3, 1)
ax1.scatter(
    kg_sources["ontology_ratio"],
    kg_sources["biolink_edge_coverage"]
)

# Annotate every point with its KG name.
for _, r in kg_sources.iterrows():
    ax1.text(
        r["ontology_ratio"],
        r["biolink_edge_coverage"],
        r["KG"],
        fontsize=8
    )

ax1.set_xlabel("Ontology : Total Source Ratio")
ax1.set_ylabel("Biolink Edge Coverage")
ax1.set_title("A. Ontology Reliance vs Biolink Coverage")

# ===== Panel B: source diversity vs edge-type entropy =====
# Tests whether KGs that pull from more sources end up with more evenly
# distributed Biolink edge types.
ax2 = fig.add_subplot(1, 3, 2)
ax2.scatter(
    kg_sources["total_sources"],
    kg_sources["edge_type_entropy"]
)

for _, r in kg_sources.iterrows():
    ax2.text(
        r["total_sources"],
        r["edge_type_entropy"],
        r["KG"],
        fontsize=8
    )

ax2.set_xlabel("Source Diversity (Total Sources)")
ax2.set_ylabel("Edge-Type Entropy")
ax2.set_title("B. Source Diversity vs Semantic Entropy")

# ===== Panel C: hierarchical clustering by source composition =====
# Cluster KGs by their (ontology_sources, non_ontology_sources,
# ontology_ratio) feature vector using Ward linkage; show the dendrogram
# on its side.
ax3 = fig.add_subplot(1, 3, 3)

features = kg_sources.set_index("KG")[
    ["ontology_sources", "non_ontology_sources", "ontology_ratio"]
]

Z = linkage(features, method="ward")

dendrogram(
    Z,
    labels=features.index,
    orientation="right",
    ax=ax3
)

ax3.set_title("C. KG Clustering by Source Composition")
ax3.set_xlabel("Distance")

plt.tight_layout()
plt.savefig(
    "kg_source_semantics_multifigure.svg",
    format="svg",
    bbox_inches="tight"
)
plt.show()

# =============================================================================
# Pass 2: 6-panel figure (Panels A-F) -> kg_source_semantics_full.svg
#
# Re-imports and re-loads the same inputs so this block can also be run
# stand-alone if the upstream cell is skipped.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import entropy, spearmanr
from scipy.cluster.hierarchy import linkage, dendrogram

# -----------------------------
# Load data
# -----------------------------
kg_sources = pd.read_csv("kg_source_counts.csv")
biolink_edges = pd.read_csv("kg_biolink_edge_matrix.csv", index_col=0)

# Normalize KG names: strip leading/trailing whitespace so the .map() call
# below joins KG identifiers correctly between the two tables.
# Normalize KG names: strip spaces and uppercase
kg_sources["KG"] = kg_sources["KG"].str.strip()
biolink_edges.columns = biolink_edges.columns.str.strip()

# -----------------------------
# Compute metrics
# -----------------------------
# Ontology ratio: ontology / total sources (per KG).
# Ontology ratio
kg_sources["ontology_ratio"] = (
    kg_sources["ontology_sources"] / kg_sources["total_sources"]
)

# Biolink edge coverage: sum of mapped Biolink predicates per KG.
# Biolink edge coverage
biolink_coverage = biolink_edges.sum(axis=0)
kg_sources["biolink_edge_coverage"] = kg_sources["KG"].map(biolink_coverage)

# Edge-type entropy: Shannon entropy (base 2) of the Biolink edge-type
# distribution within each KG. Zero when a KG has no mapped edges.
# Edge-type entropy
edge_entropy = {}
for kg in biolink_edges.columns:
    vals = biolink_edges[kg].values
    if vals.sum() == 0:
        edge_entropy[kg] = 0
    else:
        p = vals / vals.sum()
        edge_entropy[kg] = entropy(p, base=2)
kg_sources["edge_type_entropy"] = kg_sources["KG"].map(edge_entropy)

# -----------------------------
# Correlations
# -----------------------------
# Spearman rank correlations - non-parametric, robust to non-linear trends.
rho_ont_cov, p_ont_cov = spearmanr(
    kg_sources["ontology_ratio"], kg_sources["biolink_edge_coverage"]
)
rho_div_ent, p_div_ent = spearmanr(
    kg_sources["total_sources"], kg_sources["edge_type_entropy"]
)
print("Ontology ratio vs Biolink coverage: ρ =", rho_ont_cov, "p =", p_ont_cov)
print("Source diversity vs edge-type entropy: ρ =", rho_div_ent, "p =", p_div_ent)

# -----------------------------
# Figure setup (2 rows x 3 cols)
# -----------------------------
sns.set(style="white")
fig = plt.figure(figsize=(18, 12))

# ===== Panel A: Ontology ratio vs Biolink coverage =====
ax1 = fig.add_subplot(2, 3, 1)
ax1.scatter(
    kg_sources["ontology_ratio"], kg_sources["biolink_edge_coverage"], s=80, color="green"
)
for _, r in kg_sources.iterrows():
    ax1.text(r["ontology_ratio"], r["biolink_edge_coverage"], r["KG"], fontsize=8)
ax1.set_xlabel("Ontology : Total Source Ratio")
ax1.set_ylabel("Biolink Edge Coverage")
ax1.set_title("A. Ontology Reliance vs Biolink Coverage")

# ===== Panel B: Source diversity vs edge-type entropy =====
ax2 = fig.add_subplot(2, 3, 2)
ax2.scatter(
    kg_sources["total_sources"], kg_sources["edge_type_entropy"], s=80, color="blue"
)
for _, r in kg_sources.iterrows():
    ax2.text(r["total_sources"], r["edge_type_entropy"], r["KG"], fontsize=8)
ax2.set_xlabel("Total Sources")
ax2.set_ylabel("Edge-Type Entropy")
ax2.set_title("B. Source Diversity vs Semantic Entropy")

# ===== Panel C: Hierarchical clustering by source composition =====
ax3 = fig.add_subplot(2, 3, 3)
features = kg_sources.set_index("KG")[["ontology_sources", "non_ontology_sources", "ontology_ratio"]]
Z = linkage(features, method="ward")
dendrogram(Z, labels=features.index, orientation="right", ax=ax3)
ax3.set_title("C. KG Clustering by Source Composition")
ax3.set_xlabel("Distance")

# ===== Panel D: Edge-type rarefaction curves =====
# Linear-approximation rarefaction: how many Biolink edge types are
# accumulated as more of the KG's sources are added. Useful as a crude
# estimate of marginal-coverage gain per added source.
ax4 = fig.add_subplot(2, 3, 4)
for kg in biolink_edges.columns:
    # safe retrieval of total sources
    if kg not in kg_sources["KG"].values:
        continue
    sources_count = kg_sources.loc[kg_sources.KG == kg, "total_sources"].values[0]
    n_edges = biolink_edges[kg].sum()
    if sources_count == 0:
        continue
    # linear approximation of accumulation
    accumulated_edges = n_edges * np.linspace(1/sources_count, 1, sources_count)
    ax4.plot(range(1, sources_count+1), accumulated_edges, label=kg)
ax4.set_xlabel("Number of Sources Added")
ax4.set_ylabel("Accumulated Biolink Edge Types")
ax4.set_title("D. Edge-Type Rarefaction Curves")
ax4.legend(fontsize=6)

# ===== Panel E: Ontology vs non-ontology coverage (approximate) =====
# Splits each KG's Biolink edge coverage roughly between its ontology
# sources (60%) and its non-ontology sources (40%) - this is a coarse
# visual approximation, not a true attribution.
ax5 = fig.add_subplot(2, 3, 5)
# Approximate: multiply edge coverage by ratio
ax5.scatter(
    kg_sources["ontology_sources"],
    kg_sources["biolink_edge_coverage"] * 0.6,
    label="Ontology-only",
    color="blue"
)
ax5.scatter(
    kg_sources["non_ontology_sources"],
    kg_sources["biolink_edge_coverage"] * 0.4,
    label="Non-ontology",
    color="orange"
)
ax5.set_xlabel("Number of Sources")
ax5.set_ylabel("Approx. Biolink Edge Coverage")
ax5.set_title("E. Ontology vs Non-Ontology Subgraph Coverage")
ax5.legend(fontsize=6)

# ===== Panel F: placeholder for node-type alignment =====
# Reserved space for a future node-type alignment view.
ax6 = fig.add_subplot(2, 3, 6)
ax6.text(0.5, 0.5, "Node-type alignment panel\n(add later)", ha="center", va="center", fontsize=12)
ax6.set_axis_off()

plt.tight_layout()
plt.savefig("kg_source_semantics_full.svg", format="svg", bbox_inches="tight")
plt.show()
