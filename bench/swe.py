"""SWE-bench Verified track: mini-SWE-agent vs Factory Droid, same GMI model.

python -m bench.swe run --n 5 --out results/swebench/pilot          # pilot
python -m bench.swe run --n 100 --workers 3 --out results/swebench/main
python -m bench.swe report --out results/swebench/main

Per instance: pull the official SWE-bench image -> run both agents (order alternates by
instance index) in their own fresh container of that image, each behind its own metering
proxy -> extract `git diff` with one shared rule -> score each patch with the official
`swebench.harness.run_evaluation` -> remove the image.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import config as configmod
from . import proxy as proxymod
from .agents import _run, droid_selector
from .config import ROOT
from .swe_common import CONTAINER_ENV, EXTRACT_PATCH

DATASET = "SWE-bench/SWE-bench_Verified"
INSTANCES = ROOT / "swebench" / "instances.txt"

DROID_PROMPT = """<pr_description>
Consider the following PR description:
{task}
</pr_description>

Your task is to make changes to non-test files in /testbed (the current directory) so that the
issue in the PR description is resolved, in a way that is general and consistent with the codebase.
Do not modify tests or configuration files (pyproject.toml, setup.cfg, etc.). Do not commit.
The environment is already set up (use `python`; the testbed environment is active).
When you are done, stop.
"""


class Budget:
    """Process-wide GMI spend tracker. The proxies refuse new calls once the cap is hit."""

    def __init__(self, cfg, cap_usd: float, spent: float = 0.0):
        self.cfg, self.cap, self.spent = cfg, cap_usd, spent
        self.lock = threading.Lock()

    def row_cost(self, r: dict) -> float:
        unc = max(r.get("prompt_tokens", 0) - r.get("cached_tokens", 0), 0)
        return self.cfg.cost(unc, r.get("cached_tokens", 0), r.get("completion_tokens", 0))

    def add(self, row: dict) -> None:
        with self.lock:
            self.spent += self.row_cost(row)

    def allowed(self) -> bool:
        return self.spent < self.cap


def image_for(iid: str) -> str:
    return f"docker.io/swebench/sweb.eval.x86_64.{iid.replace('__', '_1776_')}:latest".lower()


def load_instances(n: int, skip: int = 0) -> list[dict]:
    from datasets import load_dataset
    order = [x for x in INSTANCES.read_text().split() if not x.startswith("#") and "__" in x]
    want = order[skip:skip + n]
    ds = {d["instance_id"]: d for d in load_dataset(DATASET, split="test") if d["instance_id"] in set(want)}
    return [ds[i] | {"order_index": order.index(i)} for i in want]


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def pull(image: str) -> None:
    for attempt in range(3):
        if sh(["docker", "image", "inspect", image]).returncode == 0:
            return
        r = sh(["docker", "pull", "-q", image], timeout=1800)
        if r.returncode == 0:
            return
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"docker pull failed: {image}: {r.stderr[-300:]}")


def run_mini(cfg, args, inst, raw: Path, base_url: str):
    task = raw / "task.md"
    task.write_text(inst["problem_statement"])
    argv = [sys.executable, "-m", "bench.swe_mini_entry", "--image", image_for(inst["instance_id"]),
            "--task-file", str(task), "--model", cfg.model_id, "--base-url", base_url,
            "--step-limit", str(args.step_limit), "--wall", str(args.wall), "--max-tokens", str(cfg.max_output_tokens),
            "--out", str(raw / "mini_result.json"), "--traj", str(raw / "trajectory.json"), "--patch", str(raw / "patch.diff")]
    env = {k: v for k, v in os.environ.items() if k not in (cfg.api_key_env, "OPENAI_API_KEY")}
    env["PYTHONPATH"] = str(ROOT)
    code, wall, to = _run(argv, ROOT, env, args.wall + 120, raw / "agent.log")
    res = json.loads((raw / "mini_result.json").read_text()) if (raw / "mini_result.json").is_file() else {}
    if to:  # killed: container may linger
        sh(["bash", "-c", "docker ps -q --filter name=minisweagent- --filter ancestor=" + image_for(inst["instance_id"])
            + " | xargs -r docker rm -f"])
    return {"wall_s": wall, "timed_out": to, "exit_code": code, "agent_status": res.get("exit_status", "crashed"),
            "agent_steps": res.get("steps"), "agent_prompt_tokens": res.get("prompt_tokens"),
            "agent_completion_tokens": res.get("completion_tokens"), "error": res.get("error")}


def run_droid(cfg, args, inst, raw: Path, base_url: str):
    image = image_for(inst["instance_id"])
    name = f"droid-{uuid.uuid4().hex[:8]}"
    settings = {"customModels": [{"model": cfg.model_id, "displayName": cfg.model_name, "baseUrl": base_url,
                                  "apiKey": "via-proxy", "provider": "generic-chat-completion-api",
                                  "maxOutputTokens": cfg.max_output_tokens}]}
    (raw / "settings.json").write_text(json.dumps(settings, indent=2))
    (raw / "prompt.md").write_text(DROID_PROMPT.format(task=inst["problem_statement"]))
    r = sh(["docker", "run", "-d", "--rm", "--name", name, "--network", "host", "-w", "/testbed", image, "sleep", "3h"])
    if r.returncode:
        raise RuntimeError(f"container start failed: {r.stderr[-300:]}")
    try:
        sh(["docker", "cp", args.droid_bin, f"{name}:/usr/local/bin/droid"], check=True)
        sh(["docker", "exec", name, "mkdir", "-p", "/root/droidhome/.factory"], check=True)
        sh(["docker", "cp", str(raw / "settings.json"), f"{name}:/root/droidhome/.factory/settings.json"], check=True)
        sh(["docker", "cp", str(raw / "prompt.md"), f"{name}:/tmp/droid_prompt.md"], check=True)
        envs = []
        for k, v in {**CONTAINER_ENV, "HOME": "/root/droidhome"}.items():
            envs += ["-e", f"{k}={v}"]
        argv = ["docker", "exec", *envs, "-w", "/testbed", name, "droid", "exec",
                "--settings", "/root/droidhome/.factory/settings.json", "--model", droid_selector(cfg.model_name),
                "--skip-permissions-unsafe", "--output-format", "json", "--cwd", "/testbed",
                "--file", "/tmp/droid_prompt.md"]
        (raw / "command.txt").write_text(" ".join(argv))
        code, wall, to = _run(argv, ROOT, dict(os.environ), args.wall, raw / "agent.log")
        if to:
            sh(["docker", "exec", name, "pkill", "-9", "-f", "droid"])
        p = sh(["docker", "exec", name, "bash", "-c", EXTRACT_PATCH], timeout=120)
        (raw / "patch.diff").write_text(p.stdout if p.returncode == 0 else "")
    finally:
        sh(["docker", "rm", "-f", name])
    from .agents import parse_droid_json
    res = parse_droid_json((raw / "agent.log").read_text(errors="replace")) or {}
    u = res.get("usage") or {}
    return {"wall_s": wall, "timed_out": to, "exit_code": code,
            "agent_status": ("timeout" if to else ("error" if res.get("is_error") else res.get("subtype", "crashed"))),
            "agent_steps": res.get("num_turns"),
            "agent_prompt_tokens": (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) if u else None,
            "agent_completion_tokens": u.get("output_tokens"),
            "error": str(res.get("result"))[:300] if res.get("is_error") else None}


def evaluate(agent: str, inst: dict, patch: str, out: Path) -> dict:
    iid = inst["instance_id"]
    if not patch.strip():
        return {"resolved": False, "eval_status": "empty_patch"}
    ev = out / "eval"
    ev.mkdir(parents=True, exist_ok=True)
    preds = ev / f"preds.{agent}.{iid}.json"
    preds.write_text(json.dumps([{"instance_id": iid, "model_name_or_path": agent, "model_patch": patch}]))
    run_id = f"{agent}"
    shutil.rmtree(ev / "logs" / "run_evaluation" / run_id / agent / iid, ignore_errors=True)
    r = sh([sys.executable, "-m", "swebench.harness.run_evaluation", "-d", DATASET, "-p", str(preds),
            "--run_id", run_id, "--max_workers", "1", "-i", iid, "-t", "1800"], cwd=ev, timeout=3600)
    rep = ev / "logs" / "run_evaluation" / run_id / agent / iid / "report.json"
    if rep.is_file():
        d = json.loads(rep.read_text())[iid]
        return {"resolved": bool(d.get("resolved")), "eval_status": "applied" if d.get("patch_successfully_applied")
                else "patch_failed", "f2p": _frac(d, "FAIL_TO_PASS"), "p2p": _frac(d, "PASS_TO_PASS")}
    return {"resolved": False, "eval_status": "eval_error", "eval_tail": (r.stdout + r.stderr)[-400:]}


def _frac(d, key):
    t = (d.get("tests_status") or {}).get(key) or {}
    s, f = len(t.get("success", [])), len(t.get("failure", []))
    return f"{s}/{s + f}"


def run_instance(cfg, args, inst, out: Path, budget: Budget, done: set, lock) -> list[dict]:
    iid, idx = inst["instance_id"], inst["order_index"]
    order = ["mini", "droid"] if idx % 2 == 0 else ["droid", "mini"]
    rows = []
    todo = [a for a in order if (iid, a) not in done and a in args.agents]
    if not todo:
        return rows
    if not budget.allowed():
        return rows
    image = image_for(iid)
    pull(image)
    for agent in todo:
        raw = out / "raw" / iid / agent
        if raw.exists():  # interrupted earlier attempt: keep its relay log so spend accounting stays complete
            dest = out / "aborted" / iid / f"{agent}-{int(time.time())}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(raw), str(dest))
        raw.mkdir(parents=True)
        spent_before = budget.spent
        meter = proxymod.MeteringProxy(cfg.base_url, raw / "requests.jsonl", api_key=os.environ.get(cfg.api_key_env),
                                       guard=budget).start()
        try:
            ar = (run_mini if agent == "mini" else run_droid)(cfg, args, inst, raw, meter.base_url)
        except Exception as e:
            ar = {"wall_s": 0, "timed_out": False, "exit_code": -1, "agent_status": "harness_error", "error": str(e)[:300]}
        finally:
            meter.stop()
        u = proxymod.summarize(raw / "requests.jsonl")
        patch = (raw / "patch.diff").read_text() if (raw / "patch.diff").is_file() else ""
        ev = evaluate(agent, inst, patch, out)
        unc = max(u["prompt_tokens"] - u["cached_tokens"], 0)
        row = {"instance_id": iid, "order_index": idx, "repo": inst["repo"], "difficulty": inst.get("difficulty"),
               "agent": agent, "ran_first": agent == order[0], **ev,
               "steps": u["ok_requests"], "requests": u["requests"], "failed_requests": u["failed_requests"],
               "prompt_tokens": u["prompt_tokens"], "cached_tokens": u["cached_tokens"],
               "completion_tokens": u["completion_tokens"],
               "cost_usd": round(cfg.cost(unc, u["cached_tokens"], u["completion_tokens"]), 6),
               "patch_lines": sum(1 for line in patch.splitlines() if line[:1] in "+-" and line[:3] not in ("+++", "---")),
               **ar, "first_api_error": u["first_error"], "model": cfg.model_id, "finished": time.time()}
        (raw / "row.json").write_text(json.dumps(row, indent=2))
        with lock:
            with (out / "runs.jsonl").open("a") as fh:
                fh.write(json.dumps(row) + "\n")
        print(f"[{time.strftime('%H:%M:%S')}] {iid:40} {agent:5} {'RESOLVED' if row['resolved'] else 'unresolved':10} "
              f"{ev['eval_status']:12} {row['wall_s']:7.1f}s {row['steps']:3} steps ${row['cost_usd']:.4f} "
              f"| total ${budget.spent:.3f}" + (f" [{(row.get('error') or row['first_api_error'] or '')[:80]}]"
                                                if (row.get('error') or row['first_api_error']) else ""), flush=True)
        rows.append(row)
    if not args.keep_images:
        sh(["docker", "rmi", "-f", image])
    return rows


def cmd_run(args) -> int:
    cfg = configmod.load()
    if args.model_id:
        cfg.model_id, cfg.model_name = args.model_id, args.display_name or args.model_id.split("/")[-1]
        cfg.price_in, cfg.price_cached, cfg.price_out = args.price_in, args.price_cached, args.price_out
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    prev = [json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines()] if (out / "runs.jsonl").is_file() else []
    done = {(r["instance_id"], r["agent"]) for r in prev if r.get("agent_status") != "harness_error"}
    budget = Budget(cfg, args.budget, 0.0)
    recorded = {(r["instance_id"], r["agent"]) for r in prev}
    # Spend = prior (outside this dir) + every relay log on disk, including aborted attempts
    # and partial runs that never wrote a row.
    relay = 0.0
    for log in list(out.glob("raw/*/*/requests.jsonl")) + list(out.glob("aborted/*/*/requests.jsonl")):
        relay += sum(budget.row_cost(json.loads(x)) for x in log.read_text().splitlines() if x.strip())
    spent_prior = args.prior_spend + relay
    budget.spent = spent_prior
    (out / "run_config.json").write_text(json.dumps({
        "model": cfg.model_id, "display_name": cfg.model_name, "prices_per_M": [cfg.price_in, cfg.price_cached, cfg.price_out],
        "n": args.n, "skip": args.skip, "workers": args.workers, "wall_s": args.wall, "mini_step_limit": args.step_limit,
        "budget_usd": args.budget, "dataset": DATASET, "instances_file": str(INSTANCES.relative_to(ROOT))}, indent=2))
    insts = load_instances(args.n, args.skip)
    print(f"{len(insts)} instances, model {cfg.model_id}, budget ${args.budget} (already spent ${spent_prior:.3f})", flush=True)
    lock = threading.Lock()
    stop = threading.Event()

    def prefetch():
        """Pull upcoming images ahead of the workers, keeping at most workers+6 on disk.
        Pulls are synchronous (3 at a time) so the on-disk count is checked after each one lands."""
        pending = [i for i in insts if not all((i["instance_id"], a) in done for a in args.agents)]
        sem = threading.Semaphore(3)

        def one(im):
            try:
                sh(["docker", "pull", "-q", im], timeout=1800)
            finally:
                sem.release()

        for inst in pending:
            while not stop.is_set():
                n = len(sh(["docker", "images", "-q", "--filter", "reference=swebench/*"]).stdout.split())
                if n < args.workers + 6:
                    break
                time.sleep(15)
            if stop.is_set() or not budget.allowed():
                return
            sem.acquire()
            threading.Thread(target=one, args=(image_for(inst["instance_id"]),), daemon=True).start()

    threading.Thread(target=prefetch, daemon=True).start()
    with ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(run_instance, cfg, args, i, out, budget, done, lock) for i in insts]
        for f in futs:
            try:
                f.result()
            except Exception as e:
                print(f"instance failed: {e}", flush=True)
    stop.set()
    print(f"done. spend this process + prior: ${budget.spent:.3f}" + ("  BUDGET CAP HIT" if not budget.allowed() else ""))
    from .swe_report import write_report
    write_report(out)
    return 0


def cmd_reeval(args) -> int:
    from datasets import load_dataset
    out = args.out.resolve()
    rows = [json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines() if x.strip()]
    latest = {(r["instance_id"], r["agent"]): r for r in rows}
    ds = {d["instance_id"]: d for d in load_dataset(DATASET, split="test")}
    changed = 0
    for key, r in latest.items():
        if not args.all and r["eval_status"] != "eval_error":
            continue
        raw = out / "raw" / r["instance_id"] / r["agent"]
        patch = (raw / "patch.diff").read_text() if (raw / "patch.diff").is_file() else ""
        pull(image_for(r["instance_id"]))
        ev = evaluate(r["agent"], ds[r["instance_id"]], patch, out)
        r.pop("eval_tail", None)
        r.update(ev)
        (raw / "row.json").write_text(json.dumps(r, indent=2))
        changed += 1
        print(r["instance_id"], r["agent"], ev, flush=True)
    (out / "runs.jsonl").write_text("".join(json.dumps(r) + "\n" for r in latest.values()))
    from .swe_report import write_report
    write_report(out)
    print(f"re-evaluated {changed}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="bench.swe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--n", type=int, default=5)
    r.add_argument("--skip", type=int, default=0)
    r.add_argument("--workers", type=int, default=1)
    r.add_argument("--wall", type=int, default=1200, help="seconds per agent per instance")
    r.add_argument("--step-limit", type=int, default=100, help="mini-swe-agent step cap")
    r.add_argument("--budget", type=float, default=20.0, help="stop calling GMI above this total USD")
    r.add_argument("--prior-spend", type=float, default=0.0, help="spend outside this out dir to count toward budget")
    r.add_argument("--agents", type=lambda s: s.split(","), default=["mini", "droid"])
    r.add_argument("--droid-bin", default=shutil.which("droid") or str(Path.home() / ".local/bin/droid"))
    r.add_argument("--keep-images", action="store_true")
    r.add_argument("--model-id")
    r.add_argument("--display-name")
    r.add_argument("--price-in", type=float)
    r.add_argument("--price-cached", type=float)
    r.add_argument("--price-out", type=float)
    r.add_argument("--out", type=Path, required=True)
    re_ = sub.add_parser("reeval", help="re-score saved patches whose evaluation errored")
    re_.add_argument("--out", type=Path, required=True)
    re_.add_argument("--all", action="store_true")
    rp = sub.add_parser("report")
    rp.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "reeval":
        return cmd_reeval(args)
    from .swe_report import write_report
    write_report(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
