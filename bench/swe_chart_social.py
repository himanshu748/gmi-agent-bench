"""High-res 16:9 social chart: python -m bench.swe_chart_social results/swebench/main"""
from __future__ import annotations

import json
import statistics
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
    rows = [json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines() if x.strip()]
    latest = {(r["instance_id"], r["agent"]): r for r in rows}
    agents = ["mini", "droid"]
    st = {}
    for a in agents:
        rs = [r for r in latest.values() if r["agent"] == a]
        tok = [r["prompt_tokens"] + r["completion_tokens"] for r in rs]
        cost = [r["cost_usd"] for r in rs]
        k = sum(r["resolved"] for r in rs)
        st[a] = {"n": len(rs), "k": k, "ci": s["agg"][a]["ci"],
                 "tok_mean": statistics.mean(tok), "tok_med": statistics.median(tok), "tok_tot": sum(tok),
                 "cost_mean": statistics.mean(cost), "cost_tot": sum(cost), "cps": sum(cost) / k,
                 "wall": statistics.median(r["wall_s"] for r in rs), "steps": statistics.median(r["steps"] for r in rs)}
    panels = [
        ("Resolved, % (95% CI)", lambda a: 100 * st[a]["k"] / st[a]["n"], lambda a: f"{st[a]['k']}/{st[a]['n']}", None),
        ("Tokens per task (mean)", lambda a: st[a]["tok_mean"],
         lambda a: f"{st[a]['tok_mean']/1e3:.0f}k", lambda a: f"median {st[a]['tok_med']/1e3:.0f}k\ntotal {st[a]['tok_tot']/1e6:.1f}M"),
        ("Cost per task, USD (mean)", lambda a: st[a]["cost_mean"],
         lambda a: f"${st[a]['cost_mean']:.4f}", lambda a: f"total ${st[a]['cost_tot']:.2f}\nper resolved ${st[a]['cps']:.4f}"),
        ("Median wall time per task (s)", lambda a: st[a]["wall"], lambda a: f"{st[a]['wall']:.0f}s", None),
    ]
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    axes = axes.flatten()
    for j, (ax, (title, val, lab, sub)) in enumerate(zip(axes, panels)):
        vals = [val(a) for a in agents]
        bars = ax.bar([LABEL[a] for a in agents], vals, color=[COLORS[a] for a in agents])
        if j == 0:
            lo = [vals[i] - 100 * st[a]["ci"][0] for i, a in enumerate(agents)]
            hi = [100 * st[a]["ci"][1] - vals[i] for i, a in enumerate(agents)]
            ax.errorbar(range(2), vals, yerr=[lo, hi], fmt="none", ecolor="black", capsize=10, elinewidth=2)
            ax.tick_params(axis="y", labelsize=13)
            ax.set_ylim(0, 110)
        else:
            ax.set_ylim(0, max(vals) * 1.35)
            ax.set_yticks([])
            ax.spines["left"].set_visible(False)
        for b, a in zip(bars, agents):
            ax.annotate(lab(a), (b.get_x() + b.get_width() / 2, b.get_height() * 0.5), ha="center", va="center",
                        fontsize=22, color="white", fontweight="bold")
            if sub:
                ax.annotate(sub(a), (b.get_x() + b.get_width() / 2, b.get_height()), ha="center", va="bottom",
                            fontsize=14, xytext=(0, 3), textcoords="offset points")
        ax.set_title(title, fontsize=17, fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=15)
    fig.suptitle(f"Same model, different harness: mini-SWE-agent vs Factory Droid\n"
                 f"SWE-bench Verified, {s['n']} random tasks, {cfg['display_name']} on GMI Cloud  (McNemar p = {s['mcnemar_p']:.3f})",
                 fontsize=20, fontweight="bold")
    fig.tight_layout()
    path = out / "chart_social.png"
    fig.savefig(path, dpi=200, facecolor="white")
    return path


if __name__ == "__main__":
    print(main(Path(sys.argv[1])))
