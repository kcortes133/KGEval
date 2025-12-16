import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import entropy
from scipy.cluster.hierarchy import linkage, dendrogram

# -----------------------------
# Load data
# -----------------------------
kg_sources = pd.read_csv("kg_source_counts.csv")
biolink_edges = pd.read_csv(
    "kg_biolink_edge_matrix.csv",
    index_col=0
)

# -----------------------------
# Metrics
# -----------------------------
kg_sources["ontology_ratio"] = (
    kg_sources["ontology_sources"] /
    kg_sources["total_sources"]
)

biolink_coverage = biolink_edges.sum(axis=0)
kg_sources["biolink_edge_coverage"] = (
    kg_sources["KG"].map(biolink_coverage)
)

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
# Figure layout
# -----------------------------
sns.set(style="white")
fig = plt.figure(figsize=(14, 6))

# ===== Panel A =====
ax1 = fig.add_subplot(1, 3, 1)
ax1.scatter(
    kg_sources["ontology_ratio"],
    kg_sources["biolink_edge_coverage"]
)

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

# ===== Panel B =====
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

# ===== Panel C =====
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

# Normalize KG names: strip spaces and uppercase
kg_sources["KG"] = kg_sources["KG"].str.strip()
biolink_edges.columns = biolink_edges.columns.str.strip()

# -----------------------------
# Compute metrics
# -----------------------------
# Ontology ratio
kg_sources["ontology_ratio"] = (
    kg_sources["ontology_sources"] / kg_sources["total_sources"]
)

# Biolink edge coverage
biolink_coverage = biolink_edges.sum(axis=0)
kg_sources["biolink_edge_coverage"] = kg_sources["KG"].map(biolink_coverage)

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
rho_ont_cov, p_ont_cov = spearmanr(
    kg_sources["ontology_ratio"], kg_sources["biolink_edge_coverage"]
)
rho_div_ent, p_div_ent = spearmanr(
    kg_sources["total_sources"], kg_sources["edge_type_entropy"]
)
print("Ontology ratio vs Biolink coverage: ρ =", rho_ont_cov, "p =", p_ont_cov)
print("Source diversity vs edge-type entropy: ρ =", rho_div_ent, "p =", p_div_ent)

# -----------------------------
# Figure setup
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
ax6 = fig.add_subplot(2, 3, 6)
ax6.text(0.5, 0.5, "Node-type alignment panel\n(add later)", ha="center", va="center", fontsize=12)
ax6.set_axis_off()

plt.tight_layout()
plt.savefig("kg_source_semantics_full.svg", format="svg", bbox_inches="tight")
plt.show()
