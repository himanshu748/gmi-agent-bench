from __future__ import annotations

import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .config import Config
from .runner import FIELDS


def load_rows(out_dir: Path) -> list[dict]:
    p = out_dir / "runs.jsonl"
    rows = [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.is_file() else []
    # keep the last record for each (agent, task, run)
    latest = {(r["agent"], r["task"], r["run"]): r for r in rows}
    return sorted(latest.values(), key=lambda r: (r["task"], r["agent"], r["run"]))


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else 0


def aggregate(rows: list[dict], agent: str) -> dict:
    rs = [r for r in rows if r["agent"] == agent]
    if not rs:
        return {}
    solved = sum(r["resolved"] for r in rs)
    cost = sum(r["cost_usd"] for r in rs)
    return {
        "runs": len(rs), "resolved": solved, "rate": solved / len(rs),
        "tests": f"{sum(r['tests_passed'] for r in rs)}/{sum(r['tests_total'] for r in rs)}",
        "tests_frac": sum(r["tests_passed"] for r in rs) / max(sum(r["tests_total"] for r in rs), 1),
        "med_wall": _med([r["wall_s"] for r in rs]), "tot_wall": sum(r["wall_s"] for r in rs),
        "med_steps": _med([r["steps"] for r in rs]),
        "med_in": _med([r["prompt_tokens"] for r in rs]), "med_out": _med([r["completion_tokens"] for r in rs]),
        "tot_tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rs),
        "cost": cost, "cost_per_solve": (cost / solved) if solved else None,
        "timeouts": sum(r["timed_out"] for r in rs), "infra": sum(1 for r in rs if r["failed_requests"]),
        "edited_tests": sum(r["edited_tests"] for r in rs),
    }


LABEL = {"mini": "mini-SWE-agent", "droid": "Factory Droid"}


def render(cfg: Config, rows: list[dict], dry_run: bool) -> str:
    agents = [a for a in ("mini", "droid") if any(r["agent"] == a for r in rows)]
    tasks = sorted({r["task"] for r in rows})
    ag = {a: aggregate(rows, a) for a in agents}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = ["# Results", ""]
    if dry_run:
        L += ["> **DRY RUN.** Both real agents were driven by a scripted mock LLM (`bench/mockllm.py`), not GMI Cloud.",
              "> These numbers test the pipeline only. They say nothing about either agent.", ""]
    L += [f"Model: **{cfg.model_name}** (`{cfg.model_id}`) via GMI Cloud, same for both agents. "
          f"Tasks: {len(tasks)}. Runs per task: {max((r['run'] for r in rows), default=0)}. Generated {now}.", "",
          "## Head to head", "",
          "| Agent | Resolved | Hidden+visible tests passed | Median wall time (s) | Median steps (LLM calls) "
          "| Median input tok | Median output tok | Total cost (USD) | Cost per solve (USD) | Timeouts | Runs w/ API errors |",
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for a in agents:
        x = ag[a]
        cps = f"{x['cost_per_solve']:.5f}" if x["cost_per_solve"] is not None else "n/a"
        L.append(f"| {LABEL[a]} | {x['resolved']}/{x['runs']} ({x['rate']:.0%}) | {x['tests']} ({x['tests_frac']:.0%}) "
                 f"| {x['med_wall']:.1f} | {x['med_steps']:.0f} | {x['med_in']:,.0f} | {x['med_out']:,.0f} "
                 f"| {x['cost']:.5f} | {cps} | {x['timeouts']} | {x['infra']} |")
    if len(agents) == 2 and all(ag.values()) and not dry_run:
        m, d = ag["mini"], ag["droid"]
        def win(lo_better, km, kd, name):
            if km == kd:
                return f"- **{name}:** tie"
            better = "mini-SWE-agent" if (km < kd) == lo_better else "Factory Droid"
            return f"- **{name}:** {better}"
        L += ["", "**Verdict (this run):**",
              win(False, m["resolved"], d["resolved"], "Score (tasks resolved)"),
              win(False, m["tests_frac"], d["tests_frac"], "Tests passed"),
              win(True, m["med_wall"], d["med_wall"], "Speed (median wall time)"),
              win(True, m["tot_tokens"], d["tot_tokens"], "Token use (total)"),
              win(True, m["cost"], d["cost"], "Cost (total)")]
    L += ["", "## Per task", "", "| Task | " + " | ".join(
        f"{LABEL[a]} resolved | {LABEL[a]} time (s) | {LABEL[a]} steps | {LABEL[a]} cost" for a in agents) + " |",
          "| --- |" + " ---: | ---: | ---: | ---: |" * len(agents)]
    for t in tasks:
        cells = []
        for a in agents:
            rs = [r for r in rows if r["task"] == t and r["agent"] == a]
            cells += [f"{sum(r['resolved'] for r in rs)}/{len(rs)}", f"{_med([r['wall_s'] for r in rs]):.1f}",
                      f"{_med([r['steps'] for r in rs]):.0f}", f"{sum(r['cost_usd'] for r in rs):.5f}"]
        L.append(f"| {t} | " + " | ".join(cells) + " |")
    L += ["", "## Per run", "",
          "| Agent | Task | Run | Pass | Tests | Time (s) | Steps | In tok | Cached | Out tok | Cost (USD) | +/- lines | Note |",
          "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for r in rows:
        note = (r.get("error") or "")[:80].replace("|", "/").replace("\n", " ")
        if r["edited_tests"]:
            note = ("edited tests (restored before scoring); " + note).strip("; ")
        L.append(f"| {LABEL[r['agent']]} | {r['task']} | {r['run']} | {'pass' if r['resolved'] else 'fail'} "
                 f"| {r['tests_passed']}/{r['tests_total']} | {r['wall_s']:.1f} | {r['steps']} | {r['prompt_tokens']:,} "
                 f"| {r['cached_tokens']:,} | {r['completion_tokens']:,} | {r['cost_usd']:.5f} "
                 f"| +{r['lines_added']}/-{r['lines_removed']} | {note} |")
    L += ["", "## How to read this", "",
          "- **Resolved**: every visible and hidden pytest test passes after the run. Visible `tests/` are restored "
          "from the original before scoring, so editing tests cannot help.",
          "- **Steps / tokens** come from the metering proxy both agents talk to (one row per chat-completions call), "
          "not from each agent's self-report. Agent-reported numbers are in `results.csv` (`agent_*` columns).",
          f"- **Cost** = uncached input x ${cfg.price_in}/M + cached input x ${cfg.price_cached}/M + output x "
          f"${cfg.price_out}/M (GMI list price in `bench.yaml`).",
          "- **Wall time** is the agent process only (no setup, no scoring)."]
    return "\n".join(L) + "\n"


def write_reports(cfg: Config, out_dir: Path, dry_run: bool) -> tuple[Path, Path]:
    rows = load_rows(out_dir)
    csv_p, md_p = out_dir / "results.csv", out_dir / "RESULTS.md"
    write_csv(rows, csv_p)
    md_p.write_text(render(cfg, rows, dry_run))
    return csv_p, md_p
