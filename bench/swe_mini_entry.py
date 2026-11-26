"""Run stock mini-swe-agent (swebench.yaml, DockerEnvironment) on one SWE-bench instance."""
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
from minisweagent.environments.docker import DockerEnvironment  # noqa: E402
from minisweagent.models.litellm_model import LitellmModel  # noqa: E402

from bench.swe_common import CONTAINER_ENV, EXTRACT_PATCH  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    for a in ("--image", "--task-file", "--model", "--base-url", "--out", "--traj", "--patch"):
        ap.add_argument(a, required=True)
    ap.add_argument("--step-limit", type=int, default=100)
    ap.add_argument("--wall", type=int, default=1200)
    ap.add_argument("--max-tokens", type=int, default=16384)
    args = ap.parse_args()

    cfg = yaml.safe_load(get_config_path("swebench.yaml").read_text())
    agent_cfg = {k: v for k, v in cfg["agent"].items() if k != "mode"}
    agent_cfg.update(step_limit=args.step_limit, cost_limit=0, wall_time_limit_seconds=args.wall)
    model_cfg = dict(cfg["model"])
    model_cfg.update(model_name=f"openai/{args.model}", cost_tracking="ignore_errors",
                     model_kwargs={"api_base": args.base_url, "api_key": "via-proxy",
                                   "max_tokens": args.max_tokens, "drop_params": True})
    env_cfg = {k: v for k, v in cfg["environment"].items() if k != "environment_class"}
    env_cfg.update(image=args.image, env={**env_cfg.get("env", {}), **CONTAINER_ENV},
                   run_args=["--rm", "--network", "host"], pull_timeout=900, container_timeout="3h")
    env = DockerEnvironment(**env_cfg)
    agent = DefaultAgent(LitellmModel(**model_cfg), env, **agent_cfg)
    exit_status, error, submission = "", None, ""
    try:
        info = agent.run(Path(args.task_file).read_text())
        exit_status, submission = info.get("exit_status", ""), info.get("submission", "")
    except Exception as e:
        exit_status, error = type(e).__name__, str(e)[:500]
    patch = ""
    try:
        out = env.execute({"command": EXTRACT_PATCH}, timeout=120)
        patch = out["output"] if out["returncode"] == 0 else ""
    except Exception as e:
        error = (error or "") + f" | patch extraction failed: {e}"
    Path(args.patch).write_text(patch)
    agent.save(Path(args.traj))
    env.cleanup()
    prompt = completion = cached = 0
    for m in agent.messages:
        usage = ((m.get("extra") or {}).get("response") or {}).get("usage") or {}
        prompt += usage.get("prompt_tokens") or 0
        completion += usage.get("completion_tokens") or 0
        cached += ((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
    Path(args.out).write_text(json.dumps({
        "exit_status": exit_status, "error": error, "steps": agent.n_calls,
        "prompt_tokens": prompt, "completion_tokens": completion, "cached_tokens": cached,
        "own_submission_chars": len(submission or ""),
    }, indent=2))


if __name__ == "__main__":
    main()
