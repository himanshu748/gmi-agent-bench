# Results

Model: **GLM-5.3 Flash** (`zai-org/GLM-5.3-Flash`) via GMI Cloud, same for both agents. Tasks: 6. Runs per task: 2. Generated 2026-11-26 13:07 UTC.

## Head to head

| Agent | Resolved | Hidden+visible tests passed | Median wall time (s) | Median steps (LLM calls) | Median input tok | Median output tok | Total cost (USD) | Cost per solve (USD) | Timeouts | Runs w/ API errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mini-SWE-agent | 12/12 (100%) | 156/156 (100%) | 61.2 | 10 | 42,852 | 3,901 | 0.02471 | 0.00206 | 0 | 0 |
| Factory Droid | 11/12 (92%) | 155/156 (99%) | 27.1 | 7 | 70,346 | 1,554 | 0.02267 | 0.00206 | 0 | 0 |

**Verdict (this run):**
- **Score (tasks resolved):** mini-SWE-agent
- **Tests passed:** mini-SWE-agent
- **Speed (median wall time):** Factory Droid
- **Token use (total):** mini-SWE-agent
- **Cost (total):** Factory Droid

## Per task

| Task | mini-SWE-agent resolved | mini-SWE-agent time (s) | mini-SWE-agent steps | mini-SWE-agent cost | Factory Droid resolved | Factory Droid time (s) | Factory Droid steps | Factory Droid cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| csv-split | 2/2 | 78.2 | 11 | 0.00470 | 2/2 | 43.3 | 8 | 0.00477 |
| deep-merge | 2/2 | 51.4 | 10 | 0.00279 | 1/2 | 21.6 | 6 | 0.00291 |
| lru-cache | 2/2 | 54.3 | 7 | 0.00185 | 2/2 | 18.2 | 6 | 0.00242 |
| merge-intervals | 2/2 | 38.4 | 10 | 0.00237 | 2/2 | 18.1 | 6 | 0.00224 |
| parse-duration | 2/2 | 90.7 | 11 | 0.00568 | 2/2 | 49.4 | 11 | 0.00570 |
| semver-compare | 2/2 | 121.4 | 12 | 0.00733 | 2/2 | 39.3 | 8 | 0.00463 |

## Per run

| Agent | Task | Run | Pass | Tests | Time (s) | Steps | In tok | Cached | Out tok | Cost (USD) | +/- lines | Note |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Factory Droid | csv-split | 1 | pass | 11/11 | 29.5 | 7 | 70,161 | 58,112 | 1,460 | 0.00214 | +42/-1 |  |
| Factory Droid | csv-split | 2 | pass | 11/11 | 57.0 | 9 | 95,583 | 90,880 | 3,656 | 0.00263 | +36/-1 |  |
| mini-SWE-agent | csv-split | 1 | pass | 11/11 | 100.4 | 10 | 47,647 | 39,936 | 4,901 | 0.00240 | +75/-2 |  |
| mini-SWE-agent | csv-split | 2 | pass | 11/11 | 55.9 | 12 | 54,373 | 46,080 | 3,941 | 0.00230 | +60/-1 |  |
| Factory Droid | deep-merge | 1 | pass | 8/8 | 24.7 | 7 | 70,530 | 67,840 | 1,649 | 0.00163 | +26/-2 |  |
| Factory Droid | deep-merge | 2 | fail | 7/8 | 18.6 | 6 | 58,936 | 56,832 | 1,064 | 0.00128 | +22/-2 |  |
| mini-SWE-agent | deep-merge | 1 | pass | 8/8 | 64.6 | 11 | 38,057 | 33,792 | 3,861 | 0.00179 | +40/-2 |  |
| mini-SWE-agent | deep-merge | 2 | pass | 8/8 | 38.2 | 8 | 19,176 | 15,360 | 1,911 | 0.00099 | +29/-2 |  |
| Factory Droid | lru-cache | 1 | pass | 9/9 | 19.7 | 6 | 58,511 | 56,320 | 824 | 0.00121 | +19/-7 |  |
| Factory Droid | lru-cache | 2 | pass | 9/9 | 16.7 | 6 | 58,541 | 56,320 | 784 | 0.00121 | +19/-7 |  |
| mini-SWE-agent | lru-cache | 1 | pass | 9/9 | 57.9 | 8 | 19,103 | 15,360 | 1,747 | 0.00095 | +31/-7 |  |
| mini-SWE-agent | lru-cache | 2 | pass | 9/9 | 50.7 | 6 | 14,503 | 11,264 | 1,969 | 0.00090 | +42/-6 |  |
| Factory Droid | merge-intervals | 1 | pass | 11/11 | 16.3 | 6 | 58,682 | 56,320 | 820 | 0.00123 | +20/-4 |  |
| Factory Droid | merge-intervals | 2 | pass | 11/11 | 19.8 | 5 | 48,306 | 46,592 | 733 | 0.00101 | +7/-3 |  |
| mini-SWE-agent | merge-intervals | 1 | pass | 11/11 | 40.3 | 10 | 27,076 | 22,272 | 2,387 | 0.00129 | +44/-7 |  |
| mini-SWE-agent | merge-intervals | 2 | pass | 11/11 | 36.6 | 9 | 22,786 | 19,200 | 2,076 | 0.00108 | +33/-7 |  |
| Factory Droid | parse-duration | 1 | pass | 20/20 | 61.4 | 15 | 174,459 | 168,192 | 4,155 | 0.00403 | +27/-3 |  |
| Factory Droid | parse-duration | 2 | pass | 20/20 | 37.4 | 7 | 72,418 | 69,632 | 1,659 | 0.00167 | +25/-3 |  |
| mini-SWE-agent | parse-duration | 1 | pass | 20/20 | 81.7 | 12 | 63,440 | 55,296 | 5,419 | 0.00280 | +63/-3 |  |
| mini-SWE-agent | parse-duration | 2 | pass | 20/20 | 99.7 | 10 | 56,001 | 48,128 | 6,290 | 0.00288 | +67/-3 |  |
| Factory Droid | semver-compare | 1 | pass | 19/19 | 33.0 | 7 | 74,100 | 70,656 | 2,766 | 0.00201 | +86/-7 |  |
| Factory Droid | semver-compare | 2 | pass | 19/19 | 45.6 | 9 | 103,128 | 98,816 | 3,251 | 0.00262 | +79/-10 |  |
| mini-SWE-agent | semver-compare | 1 | pass | 19/19 | 98.4 | 14 | 101,802 | 89,856 | 8,249 | 0.00431 | +92/-7 |  |
| mini-SWE-agent | semver-compare | 2 | pass | 19/19 | 144.4 | 11 | 64,634 | 58,368 | 6,697 | 0.00302 | +106/-8 |  |

## How to read this

- **Resolved**: every visible and hidden pytest test passes after the run. Visible `tests/` are restored from the original before scoring, so editing tests cannot help.
- **Steps / tokens** come from the metering proxy both agents talk to (one row per chat-completions call), not from each agent's self-report. Agent-reported numbers are in `results.csv` (`agent_*` columns).
- **Cost** = uncached input x $0.075/M + cached input x $0.015/M + output x $0.25/M (GMI list price in `bench.yaml`).
- **Wall time** is the agent process only (no setup, no scoring).
