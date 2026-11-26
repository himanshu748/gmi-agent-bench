"""Harness tests. No network, no GMI key, no droid needed (except the marked e2e test)."""
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

from bench import config as configmod
from bench.agents import droid_selector, droid_settings, parse_droid_json
from bench.mockllm import MockLLM
from bench.proxy import MeteringProxy, summarize
from bench.tasks import load_tasks, prepare_workdir, score, diff_stats

ROOT = Path(__file__).resolve().parent.parent


def test_config_loads():
    cfg = configmod.load()
    assert cfg.base_url.startswith("https://") and cfg.model_id
    assert cfg.cost(1_000_000, 0, 0) == pytest.approx(cfg.price_in)
    assert cfg.cost(0, 1_000_000, 1_000_000) == pytest.approx(cfg.price_cached + cfg.price_out)


def test_droid_settings_never_contain_key(monkeypatch):
    monkeypatch.setenv("GMI_API_KEY", "secret-should-not-appear")
    cfg = configmod.load()
    s = json.dumps(droid_settings(cfg, "http://127.0.0.1:1/v1"))
    assert "secret-should-not-appear" not in s
    assert droid_selector("GLM-5.3 Flash") == "custom:GLM-5.3-Flash-0"


def test_parse_droid_json_picks_result():
    text = 'noise {"type":"message"}\n{"type":"result","num_turns":3,"usage":{"input_tokens":5}}\n'
    assert parse_droid_json(text)["num_turns"] == 3
    assert parse_droid_json("no json here") is None


@pytest.mark.parametrize("task", load_tasks(), ids=lambda t: t.id)
def test_task_buggy_fails_and_solution_passes(task, tmp_path):
    work = tmp_path / "w"
    prepare_workdir(task, work)
    assert not score(task, work, 60, tmp_path / "a.xml")["resolved"]
    shutil.copytree(task.dir / "solution", work, dirs_exist_ok=True)
    s = score(task, work, 60, tmp_path / "b.xml")
    assert s["resolved"] and s["tests_passed"] == s["tests_total"] > 0


def test_editing_tests_cannot_help(tmp_path):
    task = load_tasks(["lru-cache"])[0]
    work = tmp_path / "w"
    prepare_workdir(task, work)
    (work / "tests" / "test_lru.py").write_text("def test_x():\n    assert True\n")
    assert diff_stats(work)["edited_tests"]
    assert not score(task, work, 60, tmp_path / "j.xml")["resolved"]


def test_proxy_meters_stream_and_plain(tmp_path):
    mock = MockLLM(None, "noop").start()
    proxy = MeteringProxy(mock.base_url, tmp_path / "req.jsonl", api_key="k").start()
    try:
        for stream in (False, True):
            body = json.dumps({"model": "m", "stream": stream, "messages": [{"role": "user", "content": "hi"}],
                               "tools": [{"type": "function", "function": {"name": "bash"}}]}).encode()
            req = urllib.request.Request(proxy.base_url + "/chat/completions", data=body,
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10).read()
    finally:
        proxy.stop()
        mock.stop()
    s = summarize(tmp_path / "req.jsonl")
    assert s["requests"] == 2 and s["ok_requests"] == 2 and s["completion_tokens"] == 80 and s["usage_missing"] == 0


def test_mini_end_to_end_dry_run(tmp_path):
    r = subprocess.run([sys.executable, "-m", "bench", "run", "--dry-run", "--agents", "mini", "--tasks",
                        "merge-intervals", "--runs", "1", "--out", str(tmp_path), "--fresh"],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    row = json.loads((tmp_path / "runs.jsonl").read_text().splitlines()[0])
    assert row["resolved"] and row["steps"] == 2 and row["agent_steps"] == 2
    assert (tmp_path / "RESULTS.md").read_text().startswith("# Results")


@pytest.mark.skipif(shutil.which("droid") is None, reason="droid CLI not installed")
def test_droid_end_to_end_dry_run(tmp_path):
    r = subprocess.run([sys.executable, "-m", "bench", "run", "--dry-run", "--agents", "droid", "--tasks",
                        "merge-intervals", "--runs", "1", "--out", str(tmp_path), "--fresh"],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    row = json.loads((tmp_path / "runs.jsonl").read_text().splitlines()[0])
    assert row["resolved"] and row["steps"] == 2


def test_pycache_is_not_a_test_edit(tmp_path):
    task = load_tasks(["lru-cache"])[0]
    work = tmp_path / "w"
    prepare_workdir(task, work)
    (work / "tests" / "__pycache__").mkdir()
    (work / "tests" / "__pycache__" / "x.pyc").write_bytes(b"\x00")
    d = diff_stats(work)
    assert not d["edited_tests"] and d["files_changed"] == 0
