# SWE-bench Verified results

Model: **GLM-5.3 Flash** (`zai-org/GLM-5.3-Flash`) on GMI Cloud, same for both agents. Instances: **5** paired (both agents ran), drawn in seeded random order from all 500 Verified instances (`swebench/instances.txt`). Scored with the official `swebench` harness (v5) in Docker. Generated 2026-11-26 14:35 UTC.

| Agent | Resolved | 95% CI (Wilson) | Median wall time (s) | Median steps | Median input tok | Median output tok | Total tokens | Cached share | Total cost (USD) | Cost per resolved (USD) | Empty patches | Timeouts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mini-SWE-agent | 5/5 (100%) | 57%–100% | 448 | 37 | 545,821 | 10,240 | 4.42M | 97% | 0.090 | 0.0180 | 0 | 0 |
| Factory Droid | 5/5 (100%) | 57%–100% | 163 | 17 | 245,407 | 3,138 | 1.78M | 94% | 0.038 | 0.0076 | 0 | 0 |

**Paired:** both resolved 5, only mini-SWE-agent 0, only Droid 0, neither 0. Exact McNemar test on the discordant pairs: p = 1.000 (difference not statistically significant at 0.05).

Total GMI spend recorded in this directory: **$0.128**.

## By repository

| Repo | n | mini resolved | Droid resolved |
| --- | ---: | ---: | ---: |
| django/django | 4 | 4 | 4 |
| sympy/sympy | 1 | 1 | 1 |

## Per instance

| # | Instance | Difficulty | mini | mini s | mini steps | mini $ | Droid | Droid s | Droid steps | Droid $ |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 0 | django__django-11740 | 15 min - 1 hour | ✅ | 914 | 73 | 0.0386 | ✅ | 163 | 31 | 0.0125 |
| 1 | django__django-10880 | <15 min fix | ✅ | 193 | 25 | 0.0089 | ✅ | 30 | 5 | 0.0017 |
| 2 | sympy__sympy-15809 | <15 min fix | ✅ | 994 | 37 | 0.0117 | ✅ | 288 | 17 | 0.0052 |
| 3 | django__django-16493 | 15 min - 1 hour | ✅ | 106 | 16 | 0.0030 | ✅ | 54 | 11 | 0.0029 |
| 4 | django__django-14170 | 15 min - 1 hour | ✅ | 448 | 52 | 0.0275 | ✅ | 174 | 30 | 0.0159 |

✅ resolved, ❌ patch applied but tests fail (or patch failed to apply), ∅ empty patch.

Steps and tokens come from the local metering proxy each agent talked to. Cost uses the GMI prices in `run_config.json`. Wall time is the agent only (not image pull or scoring).
