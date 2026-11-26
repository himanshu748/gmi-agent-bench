"""Chart for the SWE-bench track: python -m bench.swe_chart results/swebench/main"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LABEL = {"mini": "mini-SWE-agent", "droid": "Factory Droid"}
COLORS = {"mini": "#4C72B0", "droid": "#DD8452"}


def main(out: Path) -> Path:
    s = json.loads((out / "summary.json").read_text())
    cfg = json.loads((out / "run_config.json").read_text())
    ag = s["agg"]
    agents = ["mini", "droid"]
    panels = [
        ("Resolved (95% CI)", lambda a: 100 * ag[a]["k"] / ag[a]["n"], lambda a: f"{ag[a]['k']}/{ag[a]['n']}"),
        ("Median wall time / instance (s)", lambda a: ag[a]["wall"], lambda a: f"{ag[a]['wall']:.0f}s"),
        ("Median steps (LLM calls)", lambda a: ag[a]["steps"], lambda a: f"{ag[a]['steps']:.0f}"),
        ("Total tokens (in+out)", lambda a: ag[a]["tok"], lambda a: f"{ag[a]['tok']/1e6:.1f}M"),
        ("Total cost (USD)", lambda a: ag[a]["cost"], lambda a: f"${ag[a]['cost']:.2f}"),
    ]
    fig, axes = plt.subplots(1, 5, figsize=(17, 4))
    for j, (ax, (title, val, lab)) in enumerate(zip(axes, panels)):
        vals = [val(a) for a in agents]
        bars = ax.bar([LABEL[a] for a in agents], vals, color=[COLORS[a] for a in agents])
        if j == 0:
            lo = [vals[i] - 100 * ag[a]["ci"][0] for i, a in enumerate(agents)]
            hi = [100 * ag[a]["ci"][1] - vals[i] for i, a in enumerate(agents)]
            ax.errorbar(range(2), vals, yerr=[lo, hi], fmt="none", ecolor="black", capsize=6)
            ax.set_ylim(0, 110)
        else:
            ax.set_ylim(0, max(vals) * 1.22)
            ax.set_yticks([])
            ax.spines["left"].set_visible(False)
        for b, a in zip(bars, agents):
            ax.annotate(lab(a), (b.get_x() + b.get_width() / 2, b.get_height() / 2), ha="center", va="center",
                        fontsize=10, color="white", fontweight="bold")
        ax.set_title(title, fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=9)
    fig.suptitle(f"SWE-bench Verified ({s['n']} random instances): mini-SWE-agent vs Factory Droid, "
                 f"both on {cfg['display_name']} via GMI Cloud", fontsize=12)
    fig.tight_layout()
    path = out / "chart.png"
    fig.savefig(path, dpi=150)
    return path


if __name__ == "__main__":
    print(main(Path(sys.argv[1])))
