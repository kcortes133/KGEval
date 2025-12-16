import pandas as pd

# -----------------------------
# File paths
# -----------------------------
NON_ONTOLOGY_FILE = "nonOntologySources.csv"
ONTOLOGY_FILE = "ontologies.csv"
SOURCES_FILE = "sources.csv"

# -----------------------------
# Load source lists (FIXED)
# -----------------------------
def load_comma_separated_list(file):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    return [x.strip() for x in content.split(",") if x.strip()]

non_ontology_sources = load_comma_separated_list(NON_ONTOLOGY_FILE)
ontology_sources = load_comma_separated_list(ONTOLOGY_FILE)

# -----------------------------
# Load KG × source matrix
# -----------------------------
src_df = pd.read_csv(SOURCES_FILE)

src_df = src_df.rename(columns={src_df.columns[0]: "source"})
kg_columns = src_df.columns[1:]

# Normalize TRUE/FALSE
src_df[kg_columns] = (
    src_df[kg_columns]
    .replace({"TRUE": 1, "FALSE": 0, "": 0})
    .fillna(0)
    .astype(int)
)

src_df["source"] = src_df["source"].str.strip()

# -----------------------------
# Split ontology vs non-ontology
# -----------------------------
ontology_df = src_df[src_df["source"].isin(ontology_sources)]
non_ontology_df = src_df[src_df["source"].isin(non_ontology_sources)]

# -----------------------------
# Top 10 ontology sources
# -----------------------------
ontology_df["kg_count"] = ontology_df[kg_columns].sum(axis=1)

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
kg_ontology_counts = ontology_df[kg_columns].sum()
kg_nonontology_counts = non_ontology_df[kg_columns].sum()

kg_counts = pd.DataFrame({
    "KG": kg_columns,
    "ontology_sources": kg_ontology_counts.values,
    "non_ontology_sources": kg_nonontology_counts.values
})

kg_counts["total_sources"] = (
    kg_counts["ontology_sources"] +
    kg_counts["non_ontology_sources"]
)

kg_counts.to_csv(
    "kg_source_counts.csv", index=False
)
