from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    base_url: str
    api_key_env: str
    model_id: str
    model_name: str
    max_output_tokens: int
    price_in: float
    price_cached: float
    price_out: float
    runs: int
    wall_seconds: int
    mini_step_limit: int
    test_timeout: int
    agents: list[str]
    droid_bin: str
    droid_autonomy: str
    droid_isolate_home: bool
    mini_config: str
    tasks: list[str] = field(default_factory=list)

    def cost(self, uncached_in: int, cached_in: int, out: int) -> float:
        return (uncached_in * self.price_in + cached_in * self.price_cached + out * self.price_out) / 1e6


def load_dotenv(path: Path) -> None:
    """Minimal .env loader. Never overrides variables already exported."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def load(path: Path | None = None) -> Config:
    load_dotenv(ROOT / ".env")
    raw = yaml.safe_load((path or ROOT / "bench.yaml").read_text())
    p, m, lim, ag = raw["provider"], raw["model"], raw["limits"], raw["agents"]
    agents = [name for name in ("mini", "droid") if ag.get(name, {}).get("enabled", True)]
    return Config(
        base_url=p["base_url"].rstrip("/"),
        api_key_env=p.get("api_key_env", "GMI_API_KEY"),
        model_id=m["id"],
        model_name=m.get("display_name", m["id"]),
        max_output_tokens=int(m.get("max_output_tokens", 16384)),
        price_in=float(m["input_usd_per_million"]),
        price_cached=float(m.get("cached_input_usd_per_million", m["input_usd_per_million"])),
        price_out=float(m["output_usd_per_million"]),
        runs=int(lim.get("runs_per_task", 1)),
        wall_seconds=int(lim.get("wall_seconds", 600)),
        mini_step_limit=int(lim.get("mini_step_limit", 40)),
        test_timeout=int(lim.get("test_timeout_seconds", 120)),
        agents=agents,
        droid_bin=os.environ.get("DROID_BIN", ag.get("droid", {}).get("bin", "droid")),
        droid_autonomy=ag.get("droid", {}).get("autonomy", "medium"),
        droid_isolate_home=bool(ag.get("droid", {}).get("isolate_home", True)),
        mini_config=ag.get("mini", {}).get("config", "mini.yaml"),
        tasks=list(raw.get("tasks") or []),
    )
