# Results

> **DRY RUN.** Both real agents were driven by a scripted mock LLM (`bench/mockllm.py`), not GMI Cloud.
> These numbers test the pipeline only. They say nothing about either agent.

Model: **GLM-5.3 Flash** (`zai-org/GLM-5.3-Flash`) via GMI Cloud, same for both agents. Tasks: 6. Runs per task: 1. Generated 2026-11-26 12:38 UTC.

## Head to head

| Agent | Resolved | Hidden+visible tests passed | Median wall time (s) | Median steps (LLM calls) | Median input tok | Median output tok | Total cost (USD) | Cost per solve (USD) | Timeouts | Runs w/ API errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mini-SWE-agent | 6/6 (100%) | 78/78 (100%) | 3.3 | 2 | 2,564 | 80 | 0.00128 | 0.00021 | 0 | 0 |
| Factory Droid | 6/6 (100%) | 78/78 (100%) | 2.2 | 2 | 21,820 | 80 | 0.00994 | 0.00166 | 0 | 0 |

## Per task

| Task | mini-SWE-agent resolved | mini-SWE-agent time (s) | mini-SWE-agent steps | mini-SWE-agent cost | Factory Droid resolved | Factory Droid time (s) | Factory Droid steps | Factory Droid cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| csv-split | 1/1 | 6.0 | 2 | 0.00021 | 1/1 | 2.8 | 2 | 0.00166 |
| deep-merge | 1/1 | 3.4 | 2 | 0.00021 | 1/1 | 2.2 | 2 | 0.00165 |
| lru-cache | 1/1 | 3.5 | 2 | 0.00021 | 1/1 | 2.1 | 2 | 0.00166 |
| merge-intervals | 1/1 | 3.1 | 2 | 0.00021 | 1/1 | 1.8 | 2 | 0.00165 |
| parse-duration | 1/1 | 3.1 | 2 | 0.00021 | 1/1 | 1.9 | 2 | 0.00166 |
| semver-compare | 1/1 | 3.2 | 2 | 0.00022 | 1/1 | 2.6 | 2 | 0.00167 |

## Per run

| Agent | Task | Run | Pass | Tests | Time (s) | Steps | In tok | Cached | Out tok | Cost (USD) | +/- lines | Note |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Factory Droid | csv-split | 1 | pass | 11/11 | 2.8 | 2 | 21,840 | 0 | 80 | 0.00166 | +25/-1 |  |
| mini-SWE-agent | csv-split | 1 | pass | 11/11 | 6.0 | 2 | 2,588 | 0 | 80 | 0.00021 | +25/-1 |  |
| Factory Droid | deep-merge | 1 | pass | 8/8 | 2.2 | 2 | 21,761 | 0 | 80 | 0.00165 | +9/-2 |  |
| mini-SWE-agent | deep-merge | 1 | pass | 8/8 | 3.4 | 2 | 2,508 | 0 | 80 | 0.00021 | +9/-2 |  |
| Factory Droid | lru-cache | 1 | pass | 9/9 | 2.1 | 2 | 21,807 | 0 | 80 | 0.00166 | +18/-7 |  |
| mini-SWE-agent | lru-cache | 1 | pass | 9/9 | 3.5 | 2 | 2,556 | 0 | 80 | 0.00021 | +18/-7 |  |
| Factory Droid | merge-intervals | 1 | pass | 11/11 | 1.8 | 2 | 21,757 | 0 | 80 | 0.00165 | +9/-3 |  |
| mini-SWE-agent | merge-intervals | 1 | pass | 11/11 | 3.1 | 2 | 2,494 | 0 | 80 | 0.00021 | +9/-3 |  |
| Factory Droid | parse-duration | 1 | pass | 20/20 | 1.9 | 2 | 21,834 | 0 | 80 | 0.00166 | +14/-3 |  |
| mini-SWE-agent | parse-duration | 1 | pass | 20/20 | 3.1 | 2 | 2,573 | 0 | 80 | 0.00021 | +14/-3 |  |
| Factory Droid | semver-compare | 1 | pass | 19/19 | 2.6 | 2 | 21,977 | 0 | 80 | 0.00167 | +30/-9 |  |
| mini-SWE-agent | semver-compare | 1 | pass | 19/19 | 3.2 | 2 | 2,717 | 0 | 80 | 0.00022 | +30/-9 |  |

## How to read this

- **Resolved**: every visible and hidden pytest test passes after the run. Visible `tests/` are restored from the original before scoring, so editing tests cannot help.
- **Steps / tokens** come from the metering proxy both agents talk to (one row per chat-completions call), not from each agent's self-report. Agent-reported numbers are in `results.csv` (`agent_*` columns).
- **Cost** = uncached input x $0.075/M + cached input x $0.015/M + output x $0.25/M (GMI list price in `bench.yaml`).
- **Wall time** is the agent process only (no setup, no scoring).
