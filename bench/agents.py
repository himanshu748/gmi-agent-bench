"""Launch one agent run as a subprocess with a hard wall-clock limit."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from .config import Config


@dataclass
class AgentRun:
    exit_code: int
    wall_s: float
    timed_out: bool
    steps: int | None = None
    prompt_tokens: int | None = None      # agent-reported, total input incl. cached
    completion_tokens: int | None = None
    cached_tokens: int | None = None
    status: str = ""
    error: str | None = None


def _clean_env(cfg: Config, extra: dict | None = None) -> dict:
    env = dict(os.environ)
    # The agents talk to the local metering proxy, which injects the real key.
    # Remove it from the agent's environment so tool calls can't print it.
    for k in (cfg.api_key_env, "OPENAI_API_KEY"):
        env.pop(k, None)
    env["PATH"] = f"{Path(sys.executable).parent}:{env.get('PATH', '')}"  # python + pytest for the agent
    env.update(extra or {})
    return env


def _run(argv: list[str], cwd: Path, env: dict, timeout: int, log: Path) -> tuple[int, float, bool]:
    t0 = time.time()
    with log.open("wb") as fh:
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        try:
            code, timed_out = p.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            code, timed_out = 124, True
    return code, round(time.time() - t0, 2), timed_out


def run_mini(cfg: Config, work: Path, prompt: Path, base_url: str, raw: Path) -> AgentRun:
    out = raw / "mini_result.json"
    argv = [sys.executable, "-m", "bench.mini_entry", "--cwd", str(work), "--task-file", str(prompt),
            "--model", cfg.model_id, "--base-url", base_url, "--config", cfg.mini_config,
            "--step-limit", str(cfg.mini_step_limit), "--wall", str(cfg.wall_seconds),
            "--max-tokens", str(cfg.max_output_tokens), "--out", str(out), "--traj", str(raw / "trajectory.json")]
    (raw / "command.txt").write_text(" ".join(argv))
    env = _clean_env(cfg, {"OPENAI_API_KEY": "via-proxy", "PYTHONPATH": str(Path(__file__).parent.parent)})
    code, wall, to = _run(argv, work, env, cfg.wall_seconds + 30, raw / "agent.log")
    run = AgentRun(code, wall, to)
    if out.is_file():
        r = json.loads(out.read_text())
        run.steps, run.status, run.error = r["steps"], r["exit_status"], r["error"]
        run.prompt_tokens, run.completion_tokens, run.cached_tokens = (
            r["prompt_tokens"], r["completion_tokens"], r["cached_tokens"])
    else:
        run.status, run.error = ("timeout" if to else "crashed"), "no mini_result.json"
    return run


def droid_settings(cfg: Config, base_url: str) -> dict:
    return {"customModels": [{
        "model": cfg.model_id,
        "displayName": cfg.model_name,
        "baseUrl": base_url,
        "apiKey": "via-proxy",  # real key is injected by the proxy, never written here
        "provider": "generic-chat-completion-api",
        "maxOutputTokens": cfg.max_output_tokens,
    }]}


def droid_selector(display_name: str, index: int = 0) -> str:
    return f"custom:{display_name.replace(' ', '-')}-{index}"


def parse_droid_json(text: str) -> dict | None:
    dec, i, found = json.JSONDecoder(), 0, None
    while (i := text.find("{", i)) >= 0:
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        if isinstance(obj, dict) and obj.get("type") == "result":
            found = obj
        i = end
    return found


def run_droid(cfg: Config, work: Path, prompt: Path, base_url: str, raw: Path) -> AgentRun:
    home = raw / "home"
    (home / ".factory").mkdir(parents=True, exist_ok=True)
    settings = (home / ".factory" / "settings.json") if cfg.droid_isolate_home else (raw / "settings.json")
    settings.write_text(json.dumps(droid_settings(cfg, base_url), indent=2))
    argv = [cfg.droid_bin, "exec", "--settings", str(settings), "--model", droid_selector(cfg.model_name),
            "--auto", cfg.droid_autonomy, "--output-format", "json", "--cwd", str(work), "--file", str(prompt)]
    (raw / "command.txt").write_text(" ".join(argv))
    extra = {"HOME": str(home)} if cfg.droid_isolate_home else {}
    env = _clean_env(cfg, extra)
    env.pop("XDG_CONFIG_HOME", None)
    code, wall, to = _run(argv, work, env, cfg.wall_seconds, raw / "agent.log")
    run = AgentRun(code, wall, to)
    res = parse_droid_json((raw / "agent.log").read_text(errors="replace"))
    if res:
        u = res.get("usage") or {}
        run.steps = res.get("num_turns")
        cached = int(u.get("cache_read_input_tokens") or 0)
        run.prompt_tokens = int(u.get("input_tokens") or 0) + cached  # droid reports uncached input separately
        run.completion_tokens = int(u.get("output_tokens") or 0)
        run.cached_tokens = cached
        run.status = "error" if res.get("is_error") else res.get("subtype", "success")
        if res.get("is_error"):
            run.error = str(res.get("result"))[:500]
    else:
        run.status, run.error = ("timeout" if to else "crashed"), "no droid JSON result"
    return run


RUNNERS = {"mini": run_mini, "droid": run_droid}
