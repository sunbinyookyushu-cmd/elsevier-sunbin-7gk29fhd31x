# -*- coding: utf-8 -*-
"""ADDED FOR THIS PACKAGE (not part of the original pipeline).

Extended Data Fig. 11 (CO2_spill_placebo.png) is drawn at the end of
21b_perm_contig.py, after that script has run 500 permutations of the weight
matrix for two specifications (roughly half an hour). This file contains the
same plotting block verbatim, reading the permutation draws that 21b already
wrote to disk, so the figure can be redrawn in a second.

Inputs (all included in this folder, produced by 21b and 21):
  _spill_placebo_perm_W.csv    permuted t-statistics, contiguity and knn5
  _spill_placebo_summary.csv   actual coefficients and t-statistics
  _spill_placebo_perm.csv      inverse-distance reduced-form draws (from 21)
Output: CO2_spill_placebo.png
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"], "font.size": 11})
ACC, GRAY, INK = "#1F4E79", "#9AA0A6", "#1f1f1f"

res = pd.read_csv(os.path.join(HERE, "_spill_placebo_perm_W.csv"))
summary = pd.read_csv(os.path.join(HERE, "_spill_placebo_summary.csv"), index_col=0).T
inv = pd.read_csv(os.path.join(HERE, "_spill_placebo_perm.csv"))

fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
panels = [("Inverse distance (reduced form)", inv["rf_t"].dropna(), float(inv["rft_actual"].iloc[0])),
          ("Contiguity (joint IV)", res[res.W == "contig"]["t"].dropna(), summary["contig"]["t_actual"]),
          ("Five nearest (joint IV)", res[res.W == "knn5"]["t"].dropna(), summary["knn5"]["t_actual"])]
for ax, (ttl, s, act) in zip(axes, panels):
    ax.hist(s, bins=30, color=GRAY, edgecolor="white", linewidth=0.5)
    ax.axvline(act, color=ACC, lw=2)
    p = float((s.abs() >= abs(act)).mean())
    ax.set_title(ttl, fontsize=11, loc="left")
    ax.text(0.02, 0.95, f"actual t = {act:.2f}\npermutation p = {p:.3f}", transform=ax.transAxes, va="top", fontsize=9.5, color=INK)
    ax.set_xlabel("t-statistic on neighbour term, permuted W"); ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Draws (500)")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "CO2_spill_placebo.png"), dpi=200); plt.close(fig)
print("saved CO2_spill_placebo.png")
