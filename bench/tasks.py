from __future__ import annotations

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import ROOT

PROMPT = """You are working in a small Python repository (the current directory).
Resolve the following issue.

<issue>
{issue}
</issue>

Change the source code so the behaviour described in the issue is correct.
Hidden tests that check every point in the issue will be run after you finish,
and the existing tests in tests/ must keep passing. Do not edit or delete tests.
You can run the tests with `python -m pytest -q`. When you are done, stop.
"""


@dataclass
class Task:
    id: str
    title: str
    dir: Path

    @property
    def issue(self) -> str:
        return (self.dir / "issue.md").read_text().strip()

    def prompt(self) -> str:
        return PROMPT.format(issue=self.issue)


def load_tasks(selected: list[str] | None = None) -> list[Task]:
    tasks = []
    for d in sorted((ROOT / "tasks").iterdir()):
        if not (d / "task.yaml").is_file():
            continue
        meta = yaml.safe_load((d / "task.yaml").read_text())
        if selected and meta["id"] not in selected:
            continue
        tasks.append(Task(meta["id"], meta.get("title", meta["id"]), d))
    return tasks


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def prepare_workdir(task: Task, work: Path) -> None:
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(task.dir / "repo", work)
    git(work, "init", "-q")
    git(work, "add", "-A")
    git(work, "-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "baseline")


def _is_noise(path: str) -> bool:
    """Bytecode and tool caches are not agent edits."""
    return "__pycache__/" in path or path.endswith(".pyc") or path.startswith(".pytest_cache/")


def diff_stats(work: Path) -> dict:
    git(work, "add", "-A")
    out = git(work, "diff", "--cached", "--numstat", "HEAD")
    add = rem = 0
    files, touched_tests = [], False
    for line in out.splitlines():
        a, r, f = line.split("\t", 2)
        if _is_noise(f):
            continue
        add += int(a) if a.isdigit() else 0
        rem += int(r) if r.isdigit() else 0
        files.append(f)
        touched_tests |= f.startswith("tests/")
    (work.parent / f"{work.name}.diff").write_text(git(work, "diff", "--cached", "HEAD"))
    return {"lines_added": add, "lines_removed": rem, "files_changed": len(files), "edited_tests": touched_tests}


def score(task: Task, work: Path, timeout: int, junit: Path) -> dict:
    """Restore the original visible tests, add the hidden tests, run pytest."""
    shutil.rmtree(work / "tests", ignore_errors=True)
    shutil.copytree(task.dir / "repo" / "tests", work / "tests")
    hidden = work / "_hidden_tests"
    shutil.rmtree(hidden, ignore_errors=True)
    shutil.copytree(task.dir / "hidden_tests", hidden)
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", str(work),
           f"--junitxml={junit}", "tests", "_hidden_tests"]
    try:
        p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=timeout,
                           env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(work), "HOME": str(work)})
        code, tail = p.returncode, (p.stdout + p.stderr)[-2000:]
    except subprocess.TimeoutExpired:
        code, tail = 124, "test timeout"
    passed = total = 0
    if junit.is_file():
        try:
            root = ET.parse(junit).getroot()
            suites = [root] if root.tag == "testsuite" else list(root)
            for s in suites:
                t = int(s.get("tests", 0))
                bad = int(s.get("failures", 0)) + int(s.get("errors", 0)) + int(s.get("skipped", 0))
                total += t
                passed += t - bad
        except ET.ParseError:
            pass
    return {"tests_passed": passed, "tests_total": total, "resolved": code == 0 and total > 0 and passed == total,
            "test_output_tail": tail}
