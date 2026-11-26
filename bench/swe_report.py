"""Report for the SWE-bench Verified track: resolved rate with 95% Wilson CI, paired comparison."""
from __future__ import annotations

import csv
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

LABEL = {"mini": "mini-SWE-agent", "droid": "Factory Droid"}


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact binomial test on discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def load(out: Path) -> list[dict]:
    rows = [json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines() if x.strip()]
    latest = {(r["instance_id"], r["agent"]): r for r in rows}
    return list(latest.values())


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else 0


def write_report(out: Path) -> Path:
    out = Path(out)
    rows = load(out)
    cfg = json.loads((out / "run_config.json").read_text()) if (out / "run_config.json").is_file() else {}
    by = {(r["instance_id"], r["agent"]): r for r in rows}
    paired = sorted({i for (i, a) in by if (i, "mini") in by and (i, "droid") in by})
    P = [by[(i, a)] for i in paired for a in ("mini", "droid")]
    fields = ["instance_id", "order_index", "repo", "difficulty", "agent", "ran_first", "resolved", "eval_status",
              "f2p", "p2p", "wall_s", "timed_out", "steps", "requests", "failed_requests", "prompt_tokens",
              "cached_tokens", "completion_tokens", "cost_usd", "patch_lines", "agent_status", "agent_steps",
              "agent_prompt_tokens", "agent_completion_tokens", "error", "first_api_error"]
    with (out / "results.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["order_index"], r["agent"])))
    n = len(paired)
    agg = {}
    for a in ("mini", "droid"):
        rs = [r for r in P if r["agent"] == a]
        k = sum(r["resolved"] for r in rs)
        cost = sum(r["cost_usd"] for r in rs)
        agg[a] = {"n": len(rs), "k": k, "ci": wilson(k, len(rs)), "cost": cost,
                  "cps": cost / k if k else None, "wall": med([r["wall_s"] for r in rs]),
                  "wall_tot": sum(r["wall_s"] for r in rs), "steps": med([r["steps"] for r in rs]),
                  "in": med([r["prompt_tokens"] for r in rs]), "out": med([r["completion_tokens"] for r in rs]),
                  "tok": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rs),
                  "cached": sum(r["cached_tokens"] for r in rs) / max(sum(r["prompt_tokens"] for r in rs), 1),
                  "empty": sum(r["eval_status"] == "empty_patch" for r in rs),
                  "timeouts": sum(bool(r.get("timed_out")) for r in rs),
                  "caps": sum(r.get("agent_status") in ("TimeExceeded", "LimitsExceeded") or bool(r.get("timed_out"))
                              for r in rs),
                  "api_err": sum(1 for r in rs if r.get("failed_requests"))}
    both = sum(by[(i, "mini")]["resolved"] and by[(i, "droid")]["resolved"] for i in paired)
    only_m = sum(by[(i, "mini")]["resolved"] and not by[(i, "droid")]["resolved"] for i in paired)
    only_d = sum(by[(i, "droid")]["resolved"] and not by[(i, "mini")]["resolved"] for i in paired)
    pval = mcnemar_exact(only_m, only_d)
    total_spend = sum(r["cost_usd"] for r in rows)
    relay_spend = 0.0
    prices = cfg.get("prices_per_M", [0, 0, 0])
    for log in list(out.glob("raw/*/*/requests.jsonl")) + list(out.glob("aborted/*/*/requests.jsonl")):
        for line in log.read_text().splitlines():
            if line.strip():
                q = json.loads(line)
                unc = max(q.get("prompt_tokens", 0) - q.get("cached_tokens", 0), 0)
                relay_spend += (unc * prices[0] + q.get("cached_tokens", 0) * prices[1]
                                + q.get("completion_tokens", 0) * prices[2]) / 1e6
    L = ["# SWE-bench Verified results", "",
         f"Model: **{cfg.get('display_name', '?')}** (`{cfg.get('model', '?')}`) on GMI Cloud, same for both agents. "
         f"Instances: **{n}** paired (both agents ran), drawn in seeded random order from all 500 Verified instances "
         f"(`swebench/instances.txt`). Scored with the official `swebench` harness (v5) in Docker. "
         f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC.", "",
         "| Agent | Resolved | 95% CI (Wilson) | Median wall time (s) | Median steps | Median input tok | Median output tok | Total tokens | Cached share | Total cost (USD) | Cost per resolved (USD) | Empty patches | Hit step/time cap |",
         "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for a in ("mini", "droid"):
        x = agg[a]
        if not x["n"]:
            continue
        L.append(f"| {LABEL[a]} | {x['k']}/{x['n']} ({x['k']/x['n']:.0%}) | {x['ci'][0]:.0%}–{x['ci'][1]:.0%} "
                 f"| {x['wall']:.0f} | {x['steps']:.0f} | {x['in']:,.0f} | {x['out']:,.0f} | {x['tok']/1e6:.2f}M "
                 f"| {x['cached']:.0%} | {x['cost']:.3f} | {('%.4f' % x['cps']) if x['cps'] else 'n/a'} "
                 f"| {x['empty']} | {x['caps']} |")
    L += ["", f"**Paired:** both resolved {both}, only mini-SWE-agent {only_m}, only Droid {only_d}, neither "
          f"{n - both - only_m - only_d}. Exact McNemar test on the discordant pairs: p = {pval:.3f}"
          + (" (difference not statistically significant at 0.05)." if pval >= 0.05 else " (significant at 0.05)."),
          "", f"GMI spend: **${total_spend:.3f}** for the scored runs; **${relay_spend:.3f}** including attempts that were "
          "interrupted and rerun (every relay log under `raw/` and `aborted/`).", "",
          "## By repository", "", "| Repo | n | mini resolved | Droid resolved |", "| --- | ---: | ---: | ---: |"]
    repos = sorted({by[(i, 'mini')]["repo"] for i in paired})
    for rp in repos:
        ids = [i for i in paired if by[(i, "mini")]["repo"] == rp]
        L.append(f"| {rp} | {len(ids)} | {sum(by[(i, 'mini')]['resolved'] for i in ids)} "
                 f"| {sum(by[(i, 'droid')]['resolved'] for i in ids)} |")
    L += ["", "## Per instance", "",
          "| # | Instance | Difficulty | mini | mini s | mini steps | mini $ | Droid | Droid s | Droid steps | Droid $ |",
          "| ---: | --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |"]
    for i in sorted(paired, key=lambda i: by[(i, "mini")]["order_index"]):
        m, d = by[(i, "mini")], by[(i, "droid")]
        f = lambda r: "✅" if r["resolved"] else ("∅" if r["eval_status"] == "empty_patch" else "❌")
        L.append(f"| {m['order_index']} | {i} | {m.get('difficulty') or ''} | {f(m)} | {m['wall_s']:.0f} | {m['steps']} "
                 f"| {m['cost_usd']:.4f} | {f(d)} | {d['wall_s']:.0f} | {d['steps']} | {d['cost_usd']:.4f} |")
    L += ["", "✅ resolved, ❌ patch applied but tests fail (or patch failed to apply), ∅ empty patch.", "",
          "Steps and tokens come from the local metering proxy each agent talked to. Cost uses the GMI prices in "
          "`run_config.json`. Wall time is the agent only (not image pull or scoring)."]
    (out / "RESULTS.md").write_text("\n".join(L) + "\n")
    (out / "summary.json").write_text(json.dumps({"n": n, "agg": agg, "both": both, "only_mini": only_m,
                                                  "only_droid": only_d, "mcnemar_p": pval,
                                                  "total_spend": total_spend, "relay_spend": relay_spend}, indent=2, default=list))
    return out / "RESULTS.md"
