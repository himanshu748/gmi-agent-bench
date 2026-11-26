"""Results chart: python -m bench.chart [results_dir] -> results_dir/chart.png"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .config import ROOT, load  # noqa: E402
from .report import LABEL, aggregate, load_rows  # noqa: E402

COLORS = {"mini": "#4C72B0", "droid": "#DD8452"}


def main(out_dir: Path) -> Path:
    cfg = load()
    rows = load_rows(out_dir)
    agents = [a for a in ("mini", "droid") if any(r["agent"] == a for r in rows)]
    ag = {a: aggregate(rows, a) for a in agents}
    panels = [
        ("Tasks resolved", lambda x: x["resolved"], lambda x: f"{x['resolved']}/{x['runs']}"),
        ("Total tokens (in+out)", lambda x: x["tot_tokens"], lambda x: f"{x['tot_tokens']/1000:,.0f}k"),
        ("Total cost (USD)", lambda x: x["cost"], lambda x: f"${x['cost']:.4f}"),
        ("Median wall time / run (s)", lambda x: x["med_wall"], lambda x: f"{x['med_wall']:.0f}s"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
    for ax, (title, val, lab) in zip(axes, panels):
        vals = [val(ag[a]) for a in agents]
        bars = ax.bar([LABEL[a] for a in agents], vals, color=[COLORS[a] for a in agents])
        for b, a in zip(bars, agents):
            ax.annotate(lab(ag[a]), (b.get_x() + b.get_width() / 2, b.get_height()), ha="center", va="bottom",
                        fontsize=10, xytext=(0, 2), textcoords="offset points")
        ax.set_title(title, fontsize=11)
        ax.set_ylim(0, max(vals) * 1.2 if max(vals) else 1)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_yticks([])
        ax.tick_params(axis="x", labelsize=9)
    runs = max(r["run"] for r in rows)
    fig.suptitle(f"mini-SWE-agent vs Factory Droid | {cfg.model_name} on GMI Cloud | "
                 f"{len({r['task'] for r in rows})} tasks x {runs} runs", fontsize=12)
    fig.tight_layout()
    path = out_dir / "chart.png"
    fig.savefig(path, dpi=150)
    return path


if __name__ == "__main__":
    print(main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "latest"))
