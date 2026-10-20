"""Apply and validate the native-label -> Biolink Model (v4.4.5) mapping.

The curated mapping is the "Biolink 4.4.5 term" and "Rule" columns of the
Supplemental Table (``supplemental/node_types.csv`` and
``supplemental/edge_types.csv``). This script checks every mapped term against
the pinned Biolink Model schema (``inputs/biolink-model-4.4.5.yaml``) and writes
the mapping as CURIEs to ``outputs/``.

Rules (the "Rule" column)
- node type                               -> a Biolink class
- explicit predicate                      -> the Biolink predicate equivalent to the label
- label is a Biolink predicate            -> that predicate
- node pair, single documented relation   -> the one relation the KG documents for
                                             that node pair (e.g. "Anatomy-gene")
- internal label                          -> no_biolink_equivalent (metadata, not biology)
- unresolved                              -> unmapped: the label names only a node
                                             pair, or has no clear Biolink equivalent

Checks (any failure exits non-zero)
- every term exists in Biolink 4.4.5 and is not deprecated
- node terms are classes; edge terms are predicates (descendants of "related to")
- "label is a Biolink predicate" terms equal the label itself
- only "internal label" / "unresolved" rows may be left without a term

Outputs
- outputs/node_type_biolink_mapping.csv
- outputs/edge_type_biolink_mapping.csv
  columns: original, biolink_mapping (CURIE, "no_biolink_equivalent" or empty), rule

Run from ``src/``:  python map_biolink.py
"""
import csv
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPP, INPUTS, OUTPUTS = (os.path.join(ROOT, d) for d in ("supplemental", "inputs", "outputs"))
# Biolink Model schema pinned to v4.4.5 (CC0), copied from
# https://raw.githubusercontent.com/biolink/biolink-model/v4.4.5/biolink-model.yaml
BIOLINK_YAML = os.path.join(INPUTS, "biolink-model-4.4.5.yaml")
NONE = "no_biolink_equivalent"

Y = yaml.safe_load(open(BIOLINK_YAML, encoding="utf-8"))
assert Y["version"] == "4.4.5", f"expected Biolink 4.4.5, got {Y['version']}"
CLASSES, SLOTS = Y["classes"], Y["slots"]


def is_predicate(name):
    seen = set()
    while name and name not in seen:
        if name == "related to":
            return True
        seen.add(name)
        name = (SLOTS.get(name) or {}).get("is_a")
    return False


def class_curie(term):  # "material sample" -> biolink:MaterialSample
    special = {"rna product": "RNAProduct", "microrna": "MicroRNA",
               "noncoding rna product": "NoncodingRNAProduct"}
    return "biolink:" + special.get(term, "".join(w[:1].upper() + w[1:] for w in term.split()))


def predicate_curie(term):  # "acts upstream of" -> biolink:acts_upstream_of
    return "biolink:" + term.replace(" ", "_")


def run(kind, infile, label_col, outfile):
    errors, counts = [], {}
    rows = list(csv.DictReader(open(infile, encoding="utf-8")))
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["original", "biolink_mapping", "rule"])
        for r in rows:
            label, term, rule = r[label_col].strip(), r["Biolink 4.4.5 term"].strip(), r["Rule"].strip()
            counts[rule] = counts.get(rule, 0) + 1
            if rule == "internal label":
                if term:
                    errors.append((label, "internal label has a term"))
                w.writerow([label, NONE, rule])
                continue
            if rule == "unresolved":
                if term:
                    errors.append((label, "unresolved row has a term"))
                w.writerow([label, "", rule])
                continue
            if not term:
                errors.append((label, f"rule '{rule}' but no term"))
                continue
            if kind == "node":
                if term not in CLASSES:
                    errors.append((label, f"'{term}' is not a Biolink 4.4.5 class"))
                elif CLASSES[term].get("deprecated"):
                    errors.append((label, f"'{term}' is deprecated"))
                w.writerow([label, class_curie(term), rule])
            else:
                if term not in SLOTS:
                    errors.append((label, f"'{term}' is not a Biolink 4.4.5 slot"))
                elif SLOTS[term].get("deprecated"):
                    errors.append((label, f"'{term}' is deprecated"))
                elif not is_predicate(term):
                    errors.append((label, f"'{term}' is not a predicate"))
                if rule == "label is a Biolink predicate" and \
                        label.lower().replace("_", " ") != term:
                    errors.append((label, f"label is not the predicate '{term}'"))
                w.writerow([label, predicate_curie(term), rule])
    print(f"{kind}: {len(rows)} labels", counts)
    return errors


os.makedirs(OUTPUTS, exist_ok=True)
errors = run("node", os.path.join(SUPP, "node_types.csv"), "Node Types",
             os.path.join(OUTPUTS, "node_type_biolink_mapping.csv"))
errors += run("edge", os.path.join(SUPP, "edge_types.csv"), "Edge Types",
              os.path.join(OUTPUTS, "edge_type_biolink_mapping.csv"))
print("Biolink", Y["version"], "| errors:", errors or "none")
sys.exit(1 if errors else 0)
