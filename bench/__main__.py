"""CLI: python -m bench {check,run,report}"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from . import config as configmod
from .agents import droid_selector, droid_settings
from .report import write_reports
from .runner import default_out, run_all
from .tasks import load_tasks


def ping(cfg) -> tuple[bool, str]:
    key = os.environ.get(cfg.api_key_env)
    if not key:
        return False, f"{cfg.api_key_env} not set"
    req = urllib.request.Request(
        cfg.base_url + "/chat/completions", method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "gmi-agent-bench/0.1"},
        data=json.dumps({"model": cfg.model_id, "max_tokens": 5,
                         "messages": [{"role": "user", "content": "ping"}]}).encode())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return True, f"HTTP {r.status} OK, model answers"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.read()[:200].decode(errors='replace')}"
    except Exception as e:
        return False, str(e)


def cmd_check(cfg, args) -> int:
    ok = True
    key = os.environ.get(cfg.api_key_env)
    print(f"model           : {cfg.model_id}  ({cfg.model_name})")
    print(f"provider        : {cfg.base_url}")
    print(f"{cfg.api_key_env:16}: {'set' if key else 'MISSING'}")
    good, msg = ping(cfg)
    print(f"GMI ping        : {msg}")
    ok = good
    droid = shutil.which(cfg.droid_bin) or (cfg.droid_bin if Path(cfg.droid_bin).is_file() else None)
    print(f"droid           : {droid or 'NOT FOUND'}  selector {droid_selector(cfg.model_name)}")
    try:
        import minisweagent
        print(f"mini-swe-agent  : {minisweagent.__version__}")
    except ImportError:
        ok = False
        print("mini-swe-agent  : NOT INSTALLED (pip install -e .)")
    print(f"tasks           : {', '.join(t.id for t in load_tasks(cfg.tasks))}")
    print("droid settings  :", json.dumps(droid_settings(cfg, "http://127.0.0.1:<proxy>/v1")))
    ok = ok and bool(droid)
    print("READY for a real run" if ok else "NOT READY for a real run (dry run still works: python -m bench run --dry-run)")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="bench")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    r = sub.add_parser("run")
    r.add_argument("--dry-run", action="store_true", help="scripted mock LLM instead of GMI; real agents")
    r.add_argument("--mock-behavior", default="solve", choices=["solve", "noop"])
    r.add_argument("--agents", default=None, help="comma list: mini,droid")
    r.add_argument("--tasks", default=None, help="comma list of task ids")
    r.add_argument("--runs", type=int, default=None)
    r.add_argument("--out", type=Path, default=None)
    r.add_argument("--skip-preflight", action="store_true", help="don't ping GMI before a real run")
    r.add_argument("--fresh", action="store_true", help="delete previous results in --out first")
    rp = sub.add_parser("report")
    rp.add_argument("--out", type=Path, default=None)
    rp.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    cfg = configmod.load()

    if args.cmd == "check":
        return cmd_check(cfg, args)
    out = args.out or default_out(args.dry_run)
    if args.cmd == "run":
        if not args.dry_run and not os.environ.get(cfg.api_key_env):
            print(f"{cfg.api_key_env} is not set. Export it or use --dry-run.", file=sys.stderr)
            return 2
        if not args.dry_run and not args.skip_preflight:
            good, msg = ping(cfg)
            if not good:
                print(f"Preflight failed, not starting: GMI {msg}", file=sys.stderr)
                return 3
        if args.fresh and out.exists():
            shutil.rmtree(out)
        tasks = load_tasks(args.tasks.split(",") if args.tasks else cfg.tasks)
        agents = args.agents.split(",") if args.agents else cfg.agents
        run_all(cfg, tasks, agents, args.runs or cfg.runs, out, args.dry_run, args.mock_behavior)
    csv_p, md_p = write_reports(cfg, out, args.dry_run)
    print(f"wrote {csv_p}\nwrote {md_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
