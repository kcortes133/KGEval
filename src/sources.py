"""
sources.py
==========

Source-composition analysis for biomedical knowledge graphs (KGs).

This script characterizes the *data sources* that each surveyed KG draws
on and splits them into two classes:

    1. Ontology sources       - curated, formal vocabularies (GO, HPO,
                                MONDO, Uberon, ChEBI, etc.) listed in
                                ``ontologies.csv``.
    2. Non-ontology sources   - databases, registries, text-mining
                                outputs, clinical resources, etc., listed
                                in ``nonOntologySources.csv``.

Given a KG x source presence/absence matrix (``sources.csv``), the script:

    * Normalizes TRUE/FALSE values into 1/0 ints.
    * Splits the matrix into ontology vs. non-ontology subsets.
    * Identifies the top 10 most reused ontology sources and the top 10
      most reused non-ontology sources across the surveyed KGs.
    * Counts how many ontology, non-ontology, and total sources each KG
      uses.

Outputs (written to the working directory):

    * ``top10_ontology_sources_by_kg.csv``
    * ``top10_nonontology_sources_by_kg.csv``
    * ``kg_source_counts.csv``  - consumed downstream by
      ``additionalAnalyses.py``.

Reference
---------
Cortes et al., "Improving Biomedical Knowledge Graph Quality: A Community
Approach," arXiv:2508.21774 (2025).
"""

import pandas as pd

# -----------------------------
# File paths
# -----------------------------
# CSV listing all non-ontology data sources (one comma-separated list).
NON_ONTOLOGY_FILE = "../data/nonOntologySources.csv"
# CSV listing all ontology data sources (one comma-separated list).
ONTOLOGY_FILE = "../data/ontologies.csv"
# KG x source presence/absence matrix (rows = sources, columns = KGs).
SOURCES_FILE = "../data/Sources.csv"

# -----------------------------
# Load source lists (FIXED)
# -----------------------------
def load_comma_separated_list(file):
    """Read a single comma-separated list from a text/CSV file.

    The ontology and non-ontology source files are stored as one long
    comma-separated string (not row-per-source). This helper reads the
    whole file, splits on commas, and strips whitespace from each entry,
    skipping empty tokens.

    Parameters
    ----------
    file : str
        Path to the file containing the comma-separated list.

    Returns
    -------
    list[str]
        Cleaned list of source names.
    """
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    return [x.strip() for x in content.split(",") if x.strip()]

# Reference vocabularies used to label each row of the KG x source matrix
# as either "ontology" or "non-ontology".
non_ontology_sources = load_comma_separated_list(NON_ONTOLOGY_FILE)
ontology_sources = load_comma_separated_list(ONTOLOGY_FILE)

# -----------------------------
# Load KG x source matrix
# -----------------------------
# sources.csv: first column = source name, remaining columns = one per KG,
# with values "TRUE" / "FALSE" indicating whether the KG uses that source.
src_df = pd.read_csv(SOURCES_FILE)

# Rename the (unnamed) first column to "source" for clarity, then capture
# the remaining columns - these are the KG identifiers.
src_df = src_df.rename(columns={src_df.columns[0]: "source"})
kg_columns = src_df.columns[1:]

# Normalize TRUE/FALSE strings (and stray blanks/NaNs) into 0/1 ints so
# we can do arithmetic over the matrix.
# Normalize TRUE/FALSE
src_df[kg_columns] = (
    src_df[kg_columns]
    .replace({"TRUE": 1, "FALSE": 0, "": 0})
    .fillna(0)
    .astype(int)
)

# Strip whitespace from source names so set membership comparisons against
# the ontology / non-ontology lists behave correctly.
src_df["source"] = src_df["source"].str.strip()

# -----------------------------
# Split ontology vs non-ontology
# -----------------------------
# Two views over the same matrix - one per source category.
ontology_df = src_df[src_df["source"].isin(ontology_sources)]
non_ontology_df = src_df[src_df["source"].isin(non_ontology_sources)]

# -----------------------------
# Top 10 ontology sources
# -----------------------------
# kg_count = number of KGs that include this ontology source.
ontology_df["kg_count"] = ontology_df[kg_columns].sum(axis=1)

# Rank ontologies by reuse and keep the 10 most-shared.
top10_ontology = (
    ontology_df
    .sort_values("kg_count", ascending=False)
    .head(10)
    .drop(columns="kg_count")
)

top10_ontology.to_csv(
    "top10_ontology_sources_by_kg.csv", index=False
)

# -----------------------------
# Top 10 non-ontology sources
# -----------------------------
# Same ranking procedure for non-ontology databases / registries.
non_ontology_df["kg_count"] = non_ontology_df[kg_columns].sum(axis=1)

top10_nonontology = (
    non_ontology_df
    .sort_values("kg_count", ascending=False)
    .head(10)
    .drop(columns="kg_count")
)

top10_nonontology.to_csv(
    "top10_nonontology_sources_by_kg.csv", index=False
)

# -----------------------------
# Count sources per KG
# -----------------------------
# Per-KG totals: how many ontology and non-ontology sources each KG draws
# on. These per-KG counts feed the downstream analyses in
# ``additionalAnalyses.py`` (ontology ratio, source-diversity vs.
# entropy, Ward clustering, ...).
kg_ontology_counts = ontology_df[kg_columns].sum()
kg_nonontology_counts = non_ontology_df[kg_columns].sum()

kg_counts = pd.DataFrame({
    "KG": kg_columns,
    "ontology_sources": kg_ontology_counts.values,
    "non_ontology_sources": kg_nonontology_counts.values
})

# Convenience column: ontology + non-ontology sources used by each KG.
kg_counts["total_sources"] = (
    kg_counts["ontology_sources"] +
    kg_counts["non_ontology_sources"]
)

kg_counts.to_csv(
    "kg_source_counts.csv", index=False
)
