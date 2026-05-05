# KGEval — Evaluating Biomedical Knowledge Graphs

[![Paper](https://img.shields.io/badge/arXiv-2508.21774-b31b1b.svg)](https://arxiv.org/abs/2508.21774)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

Companion code and data for

> **Improving Biomedical Knowledge Graph Quality: A Community Approach.**
> Cortes et al. *arXiv:2508.21774* (2025). <https://arxiv.org/abs/2508.21774>

This repository contains the analysis scripts and the curated CSV inputs
used to characterize how a set of widely-used biomedical knowledge graphs
(KGs) align with one another and with the [Biolink Model](https://biolink.github.io/biolink-model/).
The analyses cover three angles:

1. **Schema coverage** — which Biolink edge types and node classes each KG
   supports (clustered heatmaps).
2. **Source composition** — the mix of ontology vs. non-ontology data
   sources each KG draws on, and the most reused sources across KGs.
3. **Cross-KG comparisons** — derived metrics (ontology ratio, Biolink
   edge coverage, edge-type entropy) and KG clustering by source
   composition.

## Surveyed knowledge graphs

The presence/absence matrices cover the following KGs:

PharmKG · Bioteque · PrimeKG · HetioNet · SPOKE · GNBR · NCATS GARD ·
Monarch KG · Clinical KG · RTX-KG2 · HRA-KG · Petagraph · Genomic KG ·
RoboKop · DrugMechDB · EmBiology · PheKnowLator

## Repository layout

```
KGEval/
├── README.md                                   <- this file
├── requirements.txt                            <- Python dependencies
├── LICENSE                                     <- MIT license
├── CITATION.cff                                <- citation metadata
│
├── src/                                        <- analysis scripts
│   ├── sources.py                              <- source-composition analysis
│   ├── mappingstest.py                         <- Biolink edge / node clustered heatmaps
│   ├── additionalAnalyses.py                   <- cross-KG metrics + multi-panel figures
│   └── clusterHeatMap.py                       <- clustermap layout sandbox
│
├── inputs/                                     <- curated CSV inputs
│   ├── Edge Types.csv                          <- KG × native edge-type presence matrix
│   ├── Node Types.csv                          <- KG × native node-type presence matrix
│   ├── Sources.csv                             <- KG × source presence matrix
│   ├── biolink_edge_mappings.csv               <- native edge type → Biolink predicate
│   ├── biolink_node_mappings.csv               <- native node type → Biolink class
│   ├── nonOntologySources.csv                  <- comma-separated list of non-ontology sources
│   └── ontologies.csv                          <- comma-separated list of ontology sources
│
├── outputs/                                    <- generated CSVs
│   ├── kg_biolink_combined_matrix.csv          <- combined Biolink edge + node matrix
│   ├── kg_biolink_edge_matrix.csv              <- Biolink-edge matrix (consumed downstream)
│   ├── kg_biolink_node_matrix.csv              <- Biolink-node matrix
│   ├── kg_edge_type_counts.csv                 <- per-KG native edge-type counts
│   ├── kg_node_type_counts.csv                 <- per-KG native node-type counts
│   ├── kg_source_counts.csv                    <- per-KG source counts (output of sources.py)
│   ├── top10_ontology_sources_by_kg.csv        <- top 10 ontology sources by KG
│   └── top10_nonontology_sources_by_kg.csv     <- top 10 non-ontology sources by KG
│
└── figures/                                    <- generated SVG figures
    ├── kg_biolink_edge_heatmap.svg
    ├── kg_biolink_node_heatmap.svg
    ├── kg_biolink_schema_heatmap.svg
    ├── kg_source_semantics_multifigure.svg
    └── kg_source_semantics_full.svg
```

## Installation

The code targets Python 3.9+ and a small standard scientific stack.

```bash
# 1. clone
git clone https://github.com/kcortes133/KGEval.git
cd KGEval

# 2. (recommended) create a virtual env
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt
```

## Running the analyses

The scripts use relative paths (`../inputs/...`) and are designed to be
run from the `src/` directory:

```bash
cd src/

# 1. Per-KG source composition + top-N source rankings
#    Inputs : inputs/Sources.csv, inputs/ontologies.csv,
#             inputs/nonOntologySources.csv
#    Outputs: kg_source_counts.csv, top10_ontology_sources_by_kg.csv,
#             top10_nonontology_sources_by_kg.csv
python sources.py

# 2. Clustered KG × Biolink heatmaps (edge types and node classes)
#    Inputs : inputs/Edge Types.csv, inputs/Node Types.csv,
#             inputs/biolink_edge_mappings.csv,
#             inputs/biolink_node_mappings.csv
#    Outputs: kg_biolink_edge_heatmap.svg, kg_biolink_node_heatmap.svg
python mappingstest.py

# 3. Cross-KG metrics + multi-panel figures
#    Inputs : kg_source_counts.csv, kg_biolink_edge_matrix.csv
#    Outputs: kg_source_semantics_multifigure.svg,
#             kg_source_semantics_full.svg
python additionalAnalyses.py
```

The scripts are independent and can be run in any order, but the natural
flow is `sources.py` → `mappingstest.py` → `additionalAnalyses.py`,
since `additionalAnalyses.py` consumes `kg_source_counts.csv` (produced
by `sources.py`) and `kg_biolink_edge_matrix.csv`.

`clusterHeatMap.py` is a layout playground (uses the seaborn `iris` demo
dataset) and is not part of the production figure pipeline.

## Inputs (`inputs/`)

| File | Description |
|------|-------------|
| `Edge Types.csv` | KG × native edge-type presence/absence matrix (TRUE/FALSE) |
| `Node Types.csv` | KG × native node-type presence/absence matrix (TRUE/FALSE) |
| `Sources.csv` | KG × data-source presence/absence matrix |
| `biolink_edge_mappings.csv` | Chat-GPT curated mapping of native edge labels → Biolink predicates |
| `biolink_node_mappings.csv` | Chat-GPT curated mapping of native node labels → Biolink classes |
| `ontologies.csv` | Comma-separated list of source names treated as ontologies |
| `nonOntologySources.csv` | Comma-separated list of source names treated as non-ontologies |

## Outputs

Generated CSVs (`outputs/`):

- `kg_source_counts.csv` — per-KG ontology / non-ontology / total source counts
- `top10_ontology_sources_by_kg.csv` — most reused ontology sources across KGs
- `top10_nonontology_sources_by_kg.csv` — most reused non-ontology sources across KGs
- `kg_biolink_edge_matrix.csv` — Biolink edge-type matrix (rows = predicates, cols = KGs)
- `kg_biolink_node_matrix.csv` — Biolink node-class matrix
- `kg_biolink_combined_matrix.csv` — combined edge + node Biolink matrix
- `kg_edge_type_counts.csv` / `kg_node_type_counts.csv` — per-KG native edge/node type counts

Generated figures (`figures/`):

- `kg_biolink_edge_heatmap.svg` — KG × Biolink edge-type clustered heatmap
- `kg_biolink_node_heatmap.svg` — KG × Biolink node-class clustered heatmap
- `kg_biolink_schema_heatmap.svg` — combined schema heatmap
- `kg_source_semantics_multifigure.svg` — 3-panel summary (A. ontology
  reliance vs Biolink coverage, B. source diversity vs edge-type entropy,
  C. KG dendrogram by source composition)
- `kg_source_semantics_full.svg` — 6-panel extended version (A–C plus
  rarefaction curves, ontology vs non-ontology subgraph coverage, and a
  reserved node-type alignment panel)

## Metrics

For each KG the analysis computes:

- **Ontology ratio** — `ontology_sources / total_sources`
- **Biolink edge coverage** — column sum of the per-KG Biolink edge matrix
- **Edge-type entropy** — Shannon entropy (base 2) of the within-KG
  Biolink-edge distribution
- **Spearman correlations** between
  (`ontology_ratio`, `biolink_edge_coverage`) and
  (`total_sources`, `edge_type_entropy`)
- **Ward-linkage hierarchical clustering** of KGs on the feature vector
  `(ontology_sources, non_ontology_sources, ontology_ratio)`

## Citation

If you use this code or the curated mappings, please cite the paper:

```bibtex
@article{cortes2025improving,
  title   = {Improving Biomedical Knowledge Graph Quality: A Community Approach},
  author  = {Cortes, Katherina G. and Sundar, Shilpa and others},
  journal = {arXiv preprint arXiv:2508.21774},
  year    = {2025},
  url     = {https://arxiv.org/abs/2508.21774}
}
```

A `CITATION.cff` file is also provided for GitHub's "Cite this repository"
button.
