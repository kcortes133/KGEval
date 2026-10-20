"""
figures_1_2.py
==============

Reproduces manuscript Figures 1 and 2 from the evaluation table.

Input
-----
* ``supplemental/scores.csv`` - one row per KG, one column per scored
  subcriterion (A.1-E.5). Values are ``Yes``, ``Partially`` or ``No``.
  Licensing (F.1) is not a yes/no criterion and is in
  ``supplemental/licensing.csv``.

Scoring rule (as in the manuscript): partial compliance counts as met.
``--strict`` counts ``Partially`` as not met instead (sensitivity analysis).

Outputs (``figures/``)
----------------------
* ``figure1_kg_evaluation.svg`` / ``.png`` - KG x subcriterion grid; blue = met,
  red = not met, hatched = partially met (counted as met).
* ``figure2_principle_counts.svg`` / ``.png`` - one panel per principle (A-E):
  number of KGs (y) meeting a given number of that principle's subcriteria (x).

Run from ``src/``::

    python figures_1_2.py            # lenient (manuscript) scoring
    python figures_1_2.py --strict   # partial counted as not met
"""
import argparse
import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORES = os.path.join(ROOT, "supplemental", "scores.csv")
FIGS = os.path.join(ROOT, "figures")

MET, NOT_MET = "#2a6fb0", "#d1495b"
INK, MUTED = "#222222", "#666666"
PRINCIPLES = {
    "A": "Access Level and Type",
    "B": "Provenance of Nodes and Edges",
    "C": "Documented Standards, Schema, and Construction",
    "D": "Update Frequency and Versioning",
    "E": "Evaluation by Metrics and Fitness for Purpose",
}
PRINCIPLE_COLORS = {"A": "#7f7f7f", "B": "#9c755f", "C": "#b07aa1", "D": "#59a14f", "E": "#edc948"}


def load(strict):
    df = pd.read_csv(SCORES).set_index("KG")
    df.columns = [c.split()[0] for c in df.columns]  # "A.1 Additional ..." -> "A.1"
    bad = set(df.values.ravel()) - {"Yes", "No", "Partially"}
    if bad:
        raise ValueError(f"unexpected score values: {bad}")
    met = df.isin(["Yes"] if strict else ["Yes", "Partially"])
    return df, met


def figure1(df, met, out):
    n_kg, n_c = df.shape
    fig, ax = plt.subplots(figsize=(0.36 * n_c + 2.6, 0.36 * n_kg + 1.6))
    for i, kg in enumerate(df.index):
        for j, c in enumerate(df.columns):
            ok = met.loc[kg, c]
            ax.add_patch(Rectangle((j + 0.05, i + 0.05), 0.9, 0.9,
                                   facecolor=MET if ok else NOT_MET, edgecolor="white", linewidth=1.5,
                                   hatch="////" if df.loc[kg, c] == "Partially" else None))
    # principle band across the top
    for j, c in enumerate(df.columns):
        ax.add_patch(Rectangle((j, -0.75), 1, 0.5, facecolor=PRINCIPLE_COLORS[c[0]], edgecolor="white"))
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_kg, -0.85)
    ax.set_xticks([j + 0.5 for j in range(n_c)])
    ax.set_xticklabels(df.columns, rotation=90, fontsize=8, color=INK)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(n_kg)])
    ax.set_yticklabels(df.index, fontsize=9, color=INK)
    ax.tick_params(length=0, pad=2)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=MET, label="Met"), Patch(facecolor=NOT_MET, label="Not met")]
    if (df == "Partially").any().any():
        handles.append(Patch(facecolor=MET, hatch="////", edgecolor="white", label="Partially met (counted as met)"))
    handles += [Patch(facecolor=PRINCIPLE_COLORS[k], label=f"{k}. {v}") for k, v in PRINCIPLES.items()]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=8)
    fig.tight_layout()
    for ext in ("svg", "png"):
        fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def figure2(met, out):
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.6), sharey=True)
    n_kg = len(met)
    for ax, (k, name) in zip(axes, PRINCIPLES.items()):
        cols = [c for c in met.columns if c.startswith(k + ".")]
        counts = met[cols].sum(axis=1).value_counts().reindex(range(len(cols) + 1), fill_value=0)
        ax.bar(counts.index, counts.values, color=MET, width=0.7, edgecolor="white", linewidth=2)
        for x, y in counts.items():
            if y:
                ax.text(x, y + 0.2, str(y), ha="center", va="bottom", fontsize=8, color=MUTED)
        ax.set_title(textwrap.fill(f"{k}. {name}", 28), fontsize=9, color=INK)
        ax.set_xticks(range(len(cols) + 1))
        ax.set_xlabel(f"Subcriteria met (of {len(cols)})", fontsize=8, color=MUTED)
        ax.set_ylim(0, n_kg + 1)
        ax.grid(axis="y", color="#e6e6e6", linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=8)
    axes[0].set_ylabel("Number of KGs", fontsize=8, color=MUTED)
    fig.tight_layout()
    for ext in ("svg", "png"):
        fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strict", action="store_true", help="count 'Partially' as not met")
    a = ap.parse_args()
    os.makedirs(FIGS, exist_ok=True)
    df, met = load(a.strict)
    sfx = "_strict" if a.strict else ""
    figure1(df, met, os.path.join(FIGS, f"figure1_kg_evaluation{sfx}"))
    figure2(met, os.path.join(FIGS, f"figure2_principle_counts{sfx}"))
    per = met.sum()
    print(f"{int(met.values.sum())} of {met.size} ratings met "
          f"({'strict' if a.strict else 'partial counted as met'})")
    print("Per-subcriterion KGs meeting it:", ", ".join(f"{c} {n}/{len(met)}" for c, n in per.items()))


if __name__ == "__main__":
    main()
