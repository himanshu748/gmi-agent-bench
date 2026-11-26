# gmi-agent-bench: mini-SWE-agent vs Factory Droid on GMI Cloud

Two coding agents, one model, the same tasks. Which one fixes more bugs, and which one burns fewer tokens doing it?

- **[mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent)**: the ~100-line, bash-only agent from the SWE-bench / SWE-agent team (stock `DefaultAgent` + `mini.yaml` prompts, v2.4.6).
- **[Factory Droid](https://factory.ai)**: Factory's terminal coding agent, run headless with `droid exec` (v1.10.0), BYOK custom model.
- **Model**: both call the same model, served by [GMI Cloud](https://www.gmicloud.ai)'s OpenAI-compatible inference API (`https://api.gmi-serving.com/v1`). Default: `zai-org/GLM-5.3-Flash`.

Built as part of the GMI Cloud Clouders ambassador programme. Tag: [@gmi_cloud](https://x.com/gmi_cloud). This project is independent; it is not made by GMI Cloud, Factory or the SWE-agent team.

## Results

> **Real run pending.** The numbers below this line will be produced by `make run` (see [Reproduce](#reproduce)).
> The table that is in `results/dry-run/` is a pipeline test with a scripted mock LLM, not a benchmark result.

<!-- RESULTS:START -->
| Agent | Resolved | Tests passed | Median wall time (s) | Median steps | Total tokens | Total cost (USD) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mini-SWE-agent | – | – | – | – | – | – |
| Factory Droid | – | – | – | – | – | – |
<!-- RESULTS:END -->

Full per-task and per-run tables: `results/latest/RESULTS.md`; raw data: `results/latest/results.csv`.

One thing the dry run already shows, because it measures the agents' real requests: **Droid's first request is roughly 10x larger than mini-SWE-agent's** (about 10.7k vs 1.2k estimated tokens, mostly Droid's system prompt and 11 tool schemas against mini's single `bash` tool). Whether Droid gets that back by needing fewer steps is what the real run answers.

## Methodology

### Task set

Six small, self-contained Python bug-fix tasks in `tasks/`. Each is a tiny repo with a bug, a user-style issue, a few visible passing tests, and **hidden tests** the agent never sees:

| Task | Bug | Hidden+visible tests |
| --- | --- | ---: |
| `semver-compare` | string comparison of versions, no pre-release / build-metadata rules | 19 |
| `merge-intervals` | touching, unsorted and nested intervals mishandled; input mutated | 11 |
| `lru-cache` | `get` doesn't refresh recency, updates evict, no validation | 9 |
| `parse-duration` | only `"XhYm"` parses; no `d`/`s`, decimals, whitespace, validation | 20 |
| `csv-split` | quoted separators and doubled quotes break (stdlib `csv` banned) | 11 |
| `deep-merge` | nested dicts replaced, input mutated, `None`-deletes missing | 8 |

`pytest tests/test_harness.py` checks that every buggy repo **fails** and every reference `solution/` **passes**, so the scorer is validated.

Why not SWE-bench? Those instances need per-repo Docker images and a much bigger budget; this is meant to be cheap enough for anyone with a GMI key to rerun in minutes. Swapping in SWE-bench Lite instances is a natural next step (mini-SWE-agent ships `mini-extra swebench`).

### Fairness controls

| Control | How |
| --- | --- |
| Same model | One `model.id` in `bench.yaml` used by both agents |
| Same prompt | Identical task prompt (`bench/tasks.py: PROMPT`), passed as mini's `task` and as Droid's `--file`. Each agent keeps its own system prompt and tools; that scaffold *is* what is being compared |
| Same starting state | Fresh copy of the task repo + `git init` baseline per run |
| Same limits | 600 s wall clock per run for both (process-group kill). mini also has its own 40-step cap; Droid has no step flag |
| Same metering | Both agents talk to a local **metering proxy** (`bench/proxy.py`) that forwards to GMI and logs every chat-completions call. Steps and tokens come from that log, not from each tool's self-report (self-reports are kept in `agent_*` CSV columns as a cross-check) |
| Same scorer | After the run the original `tests/` are restored (editing tests can't help), hidden tests are added, `pytest` runs in a clean env. Resolved = all tests pass |
| Order effects | Runs are interleaved (task 1 mini, task 1 droid, task 2 mini, ...) so provider latency drift hits both |
| Secrets | The GMI key lives only in the proxy process. It is removed from both agents' environments and is never written to Droid's settings file |

### Metrics

- **Resolved**: tasks where all visible + hidden tests pass. Also **tests passed** (partial credit).
- **Wall time**: seconds for the agent process only.
- **Steps**: successful chat-completions calls seen by the proxy.
- **Tokens**: prompt / cached / completion tokens from the provider's `usage` field.
- **Cost (USD)**: `uncached_in x input price + cached_in x cached price + out x output price`, prices in `bench.yaml` (GMI list price for GLM-5.3 Flash read 2026-11-26: $0.075 in / $0.015 cached / $0.25 out per 1M tokens; verify on the GMI console before publishing).

### Agent configuration

- mini-SWE-agent: `DefaultAgent`, `LitellmModel` with `model_name=openai/<id>` and `api_base` = proxy, `LocalEnvironment` in the task dir, built-in `mini.yaml` templates, `step_limit=40`, no cost limit (cost is computed by the harness).
- Droid: `droid exec --settings <file> --model custom:<Display-Name>-0 --auto medium --output-format json --cwd <task> --file <prompt>`, run with a fresh `HOME` so only this run's custom model (provider `generic-chat-completion-api`, per [GMI's Factory guide](https://docs.gmicloud.ai/coding-tools/factory)) is loaded. No `--skip-permissions-unsafe`.

## Reproduce

Requirements: Linux or macOS, Python 3.10+, git, a [GMI Cloud](https://console.gmicloud.ai) API key, and the Droid CLI.

```bash
git clone <this repo> && cd gmi-agent-bench
make setup                                   # venv + mini-swe-agent 2.4.6
curl -fsSL https://app.factory.ai/cli | sh   # Droid CLI (glibc Linux or macOS)
cp .env.example .env                         # put GMI_API_KEY=... in .env (or export it)

make test       # harness unit tests + end-to-end dry run of both agents (no key needed)
make dry-run    # both real agents on all 6 tasks against the scripted mock LLM
make check      # pings GMI with your key and checks droid + mini are installed
make run        # the real benchmark -> results/latest/{results.csv,RESULTS.md}
```

Options: `python -m bench run --agents mini --tasks lru-cache,csv-split --runs 3`. To try another GMI model, change `model:` in `bench.yaml` (id from the [GMI text catalog](https://docs.gmicloud.ai/model-quickstarts/text/overview) plus its prices).

Expected cost of a full run (6 tasks x 2 agents x 2 runs) on GLM-5.3 Flash: well under $1.

## Layout

```
bench.yaml            model, prices, limits
bench/
  __main__.py         CLI: check / run / report
  runner.py           per-run loop: workdir -> proxy -> agent -> diff -> score
  agents.py           mini and droid launchers (timeouts, env scrubbing, result parsing)
  mini_entry.py       runs stock mini-swe-agent in a subprocess
  proxy.py            metering proxy (streaming + non-streaming usage capture)
  mockllm.py          scripted OpenAI-compatible server for dry runs
  tasks.py            task loading, workdir prep, hidden-test scoring
  report.py           results.csv + RESULTS.md
tasks/<id>/           repo/, issue.md, hidden_tests/, solution/
results/<name>/       runs.jsonl, results.csv, RESULTS.md, raw/<task>/<agent>/run-NN/{agent.log,requests.jsonl,junit.xml,meta.json,...}
tests/                harness tests
```

## Limitations

- Six small tasks is a smoke-scale benchmark, not a leaderboard. Treat a 1-task difference as noise; run `--runs 3+` before drawing conclusions.
- One model. Agents can rank differently on other models.
- Droid makes any auxiliary model calls it wants (they are counted, since they cost money); mini makes exactly one call per step.
- Prices change; the cost column is only as current as `bench.yaml`.

## License

MIT
