"""Run mini-swe-agent once (subprocess entry point used by the harness).

Uses mini-swe-agent's own DefaultAgent + LitellmModel + LocalEnvironment and its
built-in `mini.yaml` prompts, so this is the stock scaffold, not a re-implementation.
Usage: python -m bench.mini_entry --cwd DIR --task-file F --model ID --base-url URL
       --step-limit N --wall N --max-tokens N --out result.json --traj traj.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import yaml

os.environ.setdefault("MSWEA_SILENT_STARTUP", "1")
os.environ.setdefault("MSWEA_COST_TRACKING", "ignore_errors")

from minisweagent.agents.default import DefaultAgent  # noqa: E402
from minisweagent.config import get_config_path  # noqa: E402
from minisweagent.environments.local import LocalEnvironment  # noqa: E402
from minisweagent.models.litellm_model import LitellmModel  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    for a in ("--cwd", "--task-file", "--model", "--base-url", "--out", "--traj"):
        ap.add_argument(a, required=True)
    ap.add_argument("--config", default="mini.yaml")
    ap.add_argument("--step-limit", type=int, default=40)
    ap.add_argument("--wall", type=int, default=600)
    ap.add_argument("--max-tokens", type=int, default=16384)
    args = ap.parse_args()

    cfg = yaml.safe_load(get_config_path(args.config).read_text())
    agent_cfg = {k: v for k, v in cfg.get("agent", {}).items() if k != "mode"}
    agent_cfg.update(step_limit=args.step_limit, cost_limit=0, wall_time_limit_seconds=args.wall)
    model_cfg = dict(cfg.get("model", {}))
    model_cfg.update(
        model_name=f"openai/{args.model}",
        cost_tracking="ignore_errors",
        model_kwargs={"api_base": args.base_url, "api_key": os.environ.get("OPENAI_API_KEY", "via-proxy"),
                      "max_tokens": args.max_tokens, "drop_params": True},
    )
    env_cfg = dict(cfg.get("environment", {}))
    env_cfg.pop("environment_class", None)
    env_cfg["cwd"] = args.cwd
    env_cfg.setdefault("timeout", 120)

    agent = DefaultAgent(LitellmModel(**model_cfg), LocalEnvironment(**env_cfg), **agent_cfg)
    exit_status, error = "", None
    try:
        info = agent.run(Path(args.task_file).read_text())
        exit_status = info.get("exit_status", "")
    except Exception as e:  # recorded, harness still scores the worktree
        exit_status, error = type(e).__name__, str(e)[:500]
    agent.save(Path(args.traj))

    prompt = completion = cached = 0
    for m in agent.messages:
        usage = ((m.get("extra") or {}).get("response") or {}).get("usage") or {}
        prompt += usage.get("prompt_tokens") or 0
        completion += usage.get("completion_tokens") or 0
        cached += ((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
    Path(args.out).write_text(json.dumps({
        "exit_status": exit_status, "error": error, "steps": agent.n_calls,
        "prompt_tokens": prompt, "completion_tokens": completion, "cached_tokens": cached,
    }, indent=2))


if __name__ == "__main__":
    main()
