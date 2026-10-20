# KGEval — Biomedical Knowledge Graph Transparency and Reusability

[![Paper](https://img.shields.io/badge/arXiv-2508.21774-b31b1b.svg)](https://arxiv.org/abs/2508.21774)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![bio.tools](https://img.shields.io/badge/bio.tools-kgeval-orange.svg)](https://bio.tools/kgeval)

Companion code and data for

> **Improving Biomedical Knowledge Graph Transparency and Reusability: A Community Approach.**
> Cortes et al. Preprint: *arXiv:2508.21774* (2025). <https://arxiv.org/abs/2508.21774>

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

PharmKG · Bioteque · PrimeKG · Hetionet · SPOKE · GNBR · NCATS GARD ·
Monarch KG · Clinical KG · RTX-KG2 · HRA KG · Petagraph · GenomicKB ·
ROBOKOP · DrugMechDB · EmBiology · PheKnowLator

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
│   ├── map_biolink.py                          <- applies + validates the Biolink 4.4.5 mapping
│   ├── figures_1_2.py                          <- Figures 1 and 2 from supplemental/scores.csv
│   ├── mappingstest.py                         <- Biolink edge / node clustered heatmaps
│   ├── additionalAnalyses.py                   <- cross-KG metrics + multi-panel figures
│   └── clusterHeatMap.py                       <- clustermap layout sandbox
│
├── supplemental/                               <- Supplemental Table, one CSV per tab
│   ├── scores.csv                              <- KG × subcriterion ratings (Yes / Partially / No)
│   ├── detailed_principle_analysis.csv         <- evidence and source links behind each rating
│   ├── sensitivity.csv                         <- subcriteria met per KG, partial as yes vs. as no
│   ├── licensing.csv                           <- data license per KG (criterion F.1)
│   ├── node_types.csv / edge_types.csv         <- native labels per KG + Biolink 4.4.5 term
│   ├── sources.csv                             <- sources ingested per KG
│   ├── biolink_mapping.csv                     <- original ChatGPT vs. current Biolink mapping
│   └── framework_crosswalk.csv                 <- subcriteria mapped to FAIR, TRUST, O3, HCLS
│
├── inputs/                                     <- curated CSV inputs
│   ├── Edge Types.csv                          <- KG × native edge-type presence matrix
│   ├── Node Types.csv                          <- KG × native node-type presence matrix
│   ├── Sources.csv                             <- KG × source presence matrix
│   ├── biolink_edge_mappings.csv               <- preprint (ChatGPT) edge mapping; superseded, not used
│   ├── biolink_node_mappings.csv               <- preprint (ChatGPT) node mapping; superseded, not used
│   ├── biolink-model-4.4.5.yaml                <- pinned Biolink Model schema (CC0)
│   ├── nonOntologySources.csv                  <- non-ontology sources, one per row
│   └── ontologies.csv                          <- ontology sources, one per row
│
├── outputs/                                    <- generated CSVs
│   ├── kg_biolink_combined_matrix.csv          <- combined Biolink edge + node matrix
│   ├── kg_biolink_edge_matrix.csv              <- Biolink-edge matrix (consumed downstream)
│   ├── kg_biolink_node_matrix.csv              <- Biolink-node matrix
│   ├── kg_edge_type_counts.csv                 <- per-KG native edge-type counts
│   ├── kg_node_type_counts.csv                 <- per-KG native node-type counts
│   ├── node_type_biolink_mapping.csv           <- output of map_biolink.py (130 node labels)
│   ├── edge_type_biolink_mapping.csv           <- output of map_biolink.py (343 edge labels)
│   ├── kg_source_counts.csv                    <- per-KG source counts (output of sources.py)
│   ├── top10_ontology_sources_by_kg.csv        <- top 10 ontology sources by KG
│   └── top10_nonontology_sources_by_kg.csv     <- top 10 non-ontology sources by KG
│
└── figures/                                    <- generated SVG figures
    ├── figure1_kg_evaluation.svg/.png          <- Figure 1
    ├── figure2_principle_counts.svg/.png       <- Figure 2
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

# 1. Apply and validate the Biolink mapping (Biolink Model 4.4.5)
#    Inputs : supplemental/node_types.csv, supplemental/edge_types.csv
#             ("Biolink 4.4.5 term" and "Rule" columns),
#             inputs/biolink-model-4.4.5.yaml
#    Outputs: outputs/node_type_biolink_mapping.csv,
#             outputs/edge_type_biolink_mapping.csv
#    Every term must exist in Biolink 4.4.5, not be deprecated, and be a
#    class (nodes) or predicate (edges); otherwise the script exits non-zero.
python map_biolink.py

# 2. Native type counts, Biolink matrices and clustered heatmaps (Figs 3-4)
#    Inputs : inputs/Node Types.csv, inputs/Edge Types.csv, step-1 outputs
#    Outputs: outputs/kg_{node,edge}_type_counts.csv,
#             outputs/kg_biolink_{node,edge,combined}_matrix.csv,
#             figures/kg_biolink_{node,edge,schema}_heatmap.svg
python mappingstest.py

# 3. Per-KG source composition + top-10 source rankings (Fig 5)
#    Inputs : inputs/Sources.csv, inputs/ontologies.csv,
#             inputs/nonOntologySources.csv
#    Outputs: outputs/kg_source_counts.csv,
#             outputs/top10_{ontology,nonontology}_sources_by_kg.csv
python sources.py

# 4. Cross-KG metrics + multi-panel figures
#    Inputs : outputs/kg_source_counts.csv, outputs/kg_biolink_edge_matrix.csv
#    Outputs: figures/kg_source_semantics_{multifigure,full}.svg
python additionalAnalyses.py

# 5. Figures 1 and 2 (evaluation grid and per-principle counts)
#    Input  : supplemental/scores.csv
#    Outputs: figures/figure1_kg_evaluation.{svg,png},
#             figures/figure2_principle_counts.{svg,png}
#    Partial compliance counts as met; add --strict to count it as not met.
python figures_1_2.py
```

Run them in this order: step 2 needs step 1's mapping, and step 4 needs
the outputs of steps 2 and 3.

`clusterHeatMap.py` is a layout playground (uses the seaborn `iris` demo
dataset) and is not part of the production figure pipeline.

## Evaluation data (`supplemental/`)

The 17 KGs were rated on 27 yes/no subcriteria (A.1–E.5) plus licensing (F.1).
`scores.csv` holds the ratings and `detailed_principle_analysis.csv` the
evidence for each. These CSVs are exported from the journal Supplemental
Table, one file per tab.

## Inputs (`inputs/`)

| File | Description |
|------|-------------|
| `Edge Types.csv` | KG × native edge-type presence/absence matrix (TRUE/FALSE) |
| `Node Types.csv` | KG × native node-type presence/absence matrix (TRUE/FALSE) |
| `Sources.csv` | KG × data-source presence/absence matrix |
| `biolink_edge_mappings.csv` | Preprint (ChatGPT-assisted) edge mapping, kept for reference; superseded by the Supplemental Table mapping and not used by the scripts. `supplemental/biolink_mapping.csv` compares the two label by label. |
| `biolink_node_mappings.csv` | Preprint (ChatGPT-assisted) node mapping, kept for reference; superseded and not used by the scripts. |
| `biolink-model-4.4.5.yaml` | Biolink Model schema v4.4.5, used by `map_biolink.py` for validation |
| `ontologies.csv` | Source names treated as ontologies (one per row, header `source`) |
| `nonOntologySources.csv` | Source names treated as non-ontologies (one per row, header `source`); every source in `Sources.csv` must appear in exactly one of the two lists |

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
@article{cortes2025kgeval,
  title   = {Improving Biomedical Knowledge Graph Transparency and Reusability: A Community Approach},
  author  = {Cortes, Katherina G. and Sundar, Shilpa and Gehrke, Sarah and Manpearl, Keenan and
             Lin, Junxia and Korn, Daniel Robert and Caufield, Harry and Schaper, Kevin and
             Reese, Justin and Oshunyinka, Damilola and Koirala, Kushal and Hunter, Lawrence E. and
             Carter, E. Kathleen and DeLuca, Marcello and Krishnan, Arjun and Mungall, Chris and
             Haendel, Melissa},
  journal = {arXiv preprint arXiv:2508.21774},
  year    = {2025},
  doi     = {10.48550/arXiv.2508.21774}
}
```

A `CITATION.cff` file is also provided for GitHub's "Cite this repository"
button.

## License

Code and curated data in this repository are released under the [MIT License](LICENSE).
The bundled Biolink Model schema (`inputs/biolink-model-4.4.5.yaml`) is CC0.
