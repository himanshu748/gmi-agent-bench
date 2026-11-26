from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import asdict
from pathlib import Path

from . import proxy as proxymod
from .agents import RUNNERS
from .config import ROOT, Config
from .mockllm import MockLLM
from .tasks import Task, diff_stats, prepare_workdir, score

FIELDS = ["agent", "task", "run", "resolved", "tests_passed", "tests_total", "wall_s", "timed_out",
          "steps", "requests", "failed_requests", "prompt_tokens", "cached_tokens", "completion_tokens",
          "cost_usd", "agent_steps", "agent_prompt_tokens", "agent_completion_tokens", "lines_added",
          "lines_removed", "files_changed", "edited_tests", "agent_status", "exit_code", "error"]


def run_one(cfg: Config, agent: str, task: Task, run_idx: int, out_dir: Path, dry_run: bool,
            mock_behavior: str = "solve") -> dict:
    raw = out_dir / "raw" / task.id / agent / f"run-{run_idx:02d}"
    if raw.exists():
        shutil.rmtree(raw)
    raw.mkdir(parents=True)
    work = out_dir / "work" / task.id / agent / f"run-{run_idx:02d}"
    work.parent.mkdir(parents=True, exist_ok=True)
    prepare_workdir(task, work)
    prompt = raw / "prompt.md"
    prompt.write_text(task.prompt())

    mock = None
    if dry_run:
        mock = MockLLM(task.dir / "solution", mock_behavior).start()
        upstream, key = mock.base_url, None
    else:
        upstream, key = cfg.base_url, os.environ.get(cfg.api_key_env)
    meter = proxymod.MeteringProxy(upstream, raw / "requests.jsonl", api_key=key).start()
    try:
        ar = RUNNERS[agent](cfg, work, prompt, meter.base_url, raw)
    finally:
        meter.stop()
        if mock:
            mock.stop()

    usage = proxymod.summarize(raw / "requests.jsonl")
    d = diff_stats(work)
    s = score(task, work, cfg.test_timeout, raw / "junit.xml")
    (raw / "test_output.txt").write_text(s.pop("test_output_tail"))
    uncached = max(usage["prompt_tokens"] - usage["cached_tokens"], 0)
    row = {
        "agent": agent, "task": task.id, "run": run_idx,
        "resolved": s["resolved"], "tests_passed": s["tests_passed"], "tests_total": s["tests_total"],
        "wall_s": ar.wall_s, "timed_out": ar.timed_out,
        "steps": usage["ok_requests"], "requests": usage["requests"], "failed_requests": usage["failed_requests"],
        "prompt_tokens": usage["prompt_tokens"], "cached_tokens": usage["cached_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "cost_usd": round(cfg.cost(uncached, usage["cached_tokens"], usage["completion_tokens"]), 6),
        "agent_steps": ar.steps, "agent_prompt_tokens": ar.prompt_tokens,
        "agent_completion_tokens": ar.completion_tokens,
        **d, "agent_status": ar.status, "exit_code": ar.exit_code,
        "error": ar.error or usage["first_error"],
    }
    (raw / "meta.json").write_text(json.dumps({"row": row, "agent_run": asdict(ar), "usage": usage,
                                               "dry_run": dry_run, "model": cfg.model_id,
                                               "finished": time.time()}, indent=2))
    return row


def run_all(cfg: Config, tasks: list[Task], agents: list[str], runs: int, out_dir: Path, dry_run: bool,
            mock_behavior: str = "solve", log=print) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "runs.jsonl"
    rows = []
    # Interleave agents per task/run so provider load drifts affect both equally.
    for r in range(1, runs + 1):
        for task in tasks:
            for agent in agents:
                row = run_one(cfg, agent, task, r, out_dir, dry_run, mock_behavior)
                rows.append(row)
                with jsonl.open("a") as fh:
                    fh.write(json.dumps(row) + "\n")
                log(f"[{agent:5}] {task.id:16} run {r}: {'PASS' if row['resolved'] else 'fail'} "
                    f"{row['tests_passed']}/{row['tests_total']} tests, {row['wall_s']}s, {row['steps']} steps, "
                    f"{row['prompt_tokens']}+{row['completion_tokens']} tok, ${row['cost_usd']:.5f}"
                    + (f"  [{row['error'][:120]}]" if row["error"] else ""))
    return rows


def default_out(dry_run: bool) -> Path:
    return ROOT / "results" / ("dry-run" if dry_run else "latest")
