# SWE-bench Verified results

Model: **GLM-5.3 Flash** (`zai-org/GLM-5.3-Flash`) on GMI Cloud, same for both agents. Instances: **100** paired (both agents ran), drawn in seeded random order from all 500 Verified instances (`swebench/instances.txt`). Scored with the official `swebench` harness (v5) in Docker. Generated 2026-11-26 17:14 UTC.

| Agent | Resolved | 95% CI (Wilson) | Median wall time (s) | Median steps | Median input tok | Median output tok | Total tokens | Cached share | Total cost (USD) | Cost per resolved (USD) | Empty patches | Hit step/time cap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mini-SWE-agent | 95/100 (95%) | 89%–98% | 285 | 30 | 438,822 | 11,397 | 79.71M | 97% | 1.653 | 0.0174 | 0 | 5 |
| Factory Droid | 88/100 (88%) | 80%–93% | 132 | 18 | 277,413 | 4,850 | 47.10M | 96% | 0.976 | 0.0111 | 0 | 0 |

**Paired:** both resolved 87, only mini-SWE-agent 8, only Droid 1, neither 4. Exact McNemar test on the discordant pairs: p = 0.039 (significant at 0.05).

GMI spend: **$2.629** for the scored runs; **$2.792** including attempts that were interrupted and rerun (every relay log under `raw/` and `aborted/`).

## By repository

| Repo | n | mini resolved | Droid resolved |
| --- | ---: | ---: | ---: |
| astropy/astropy | 5 | 5 | 5 |
| django/django | 43 | 41 | 35 |
| matplotlib/matplotlib | 6 | 6 | 6 |
| psf/requests | 1 | 0 | 0 |
| pydata/xarray | 4 | 4 | 4 |
| pylint-dev/pylint | 1 | 1 | 1 |
| pytest-dev/pytest | 2 | 2 | 2 |
| scikit-learn/scikit-learn | 9 | 8 | 8 |
| sphinx-doc/sphinx | 11 | 10 | 10 |
| sympy/sympy | 18 | 18 | 17 |

## Per instance

| # | Instance | Difficulty | mini | mini s | mini steps | mini $ | Droid | Droid s | Droid steps | Droid $ |
| ---: | --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 0 | django__django-11740 | 15 min - 1 hour | ✅ | 914 | 73 | 0.0386 | ✅ | 163 | 31 | 0.0125 |
| 1 | django__django-10880 | <15 min fix | ✅ | 193 | 25 | 0.0089 | ✅ | 30 | 5 | 0.0017 |
| 2 | sympy__sympy-15809 | <15 min fix | ✅ | 994 | 37 | 0.0117 | ✅ | 288 | 17 | 0.0052 |
| 3 | django__django-16493 | 15 min - 1 hour | ✅ | 106 | 16 | 0.0030 | ✅ | 54 | 11 | 0.0029 |
| 4 | django__django-14170 | 15 min - 1 hour | ✅ | 448 | 52 | 0.0275 | ✅ | 174 | 30 | 0.0159 |
| 5 | sphinx-doc__sphinx-7440 | <15 min fix | ✅ | 695 | 43 | 0.0196 | ✅ | 211 | 38 | 0.0157 |
| 6 | django__django-14373 | <15 min fix | ✅ | 84 | 14 | 0.0032 | ✅ | 44 | 12 | 0.0022 |
| 7 | scikit-learn__scikit-learn-11578 | 15 min - 1 hour | ✅ | 150 | 16 | 0.0072 | ✅ | 79 | 9 | 0.0035 |
| 8 | django__django-11880 | <15 min fix | ✅ | 194 | 21 | 0.0042 | ✅ | 60 | 13 | 0.0029 |
| 9 | django__django-12741 | <15 min fix | ✅ | 37 | 7 | 0.0010 | ✅ | 47 | 11 | 0.0023 |
| 10 | matplotlib__matplotlib-22719 | <15 min fix | ✅ | 268 | 22 | 0.0089 | ✅ | 183 | 24 | 0.0095 |
| 11 | sympy__sympy-15349 | 15 min - 1 hour | ✅ | 161 | 20 | 0.0069 | ✅ | 97 | 15 | 0.0048 |
| 12 | django__django-17084 | 15 min - 1 hour | ✅ | 623 | 55 | 0.0247 | ✅ | 313 | 27 | 0.0107 |
| 13 | sympy__sympy-19495 | <15 min fix | ✅ | 706 | 42 | 0.0253 | ✅ | 843 | 74 | 0.0679 |
| 14 | scikit-learn__scikit-learn-26323 | 15 min - 1 hour | ✅ | 113 | 12 | 0.0032 | ✅ | 51 | 11 | 0.0027 |
| 15 | django__django-15127 | <15 min fix | ✅ | 417 | 26 | 0.0109 | ❌ | 76 | 13 | 0.0037 |
| 16 | django__django-11149 | 15 min - 1 hour | ✅ | 771 | 55 | 0.0245 | ✅ | 192 | 27 | 0.0108 |
| 17 | sympy__sympy-12489 | 1-4 hours | ✅ | 458 | 38 | 0.0205 | ❌ | 362 | 25 | 0.0119 |
| 18 | sympy__sympy-17139 | <15 min fix | ✅ | 249 | 18 | 0.0045 | ✅ | 48 | 7 | 0.0019 |
| 19 | sphinx-doc__sphinx-9698 | <15 min fix | ✅ | 155 | 22 | 0.0044 | ✅ | 33 | 7 | 0.0017 |
| 20 | django__django-10554 | 1-4 hours | ✅ | 933 | 71 | 0.0548 | ✅ | 555 | 76 | 0.0477 |
| 21 | django__django-16661 | 15 min - 1 hour | ✅ | 420 | 34 | 0.0152 | ✅ | 177 | 17 | 0.0074 |
| 22 | scikit-learn__scikit-learn-13135 | <15 min fix | ✅ | 278 | 22 | 0.0112 | ✅ | 29 | 5 | 0.0015 |
| 23 | pylint-dev__pylint-6386 | 15 min - 1 hour | ✅ | 436 | 39 | 0.0155 | ✅ | 308 | 55 | 0.0242 |
| 24 | django__django-14434 | 15 min - 1 hour | ✅ | 195 | 42 | 0.0104 | ✅ | 64 | 17 | 0.0040 |
| 25 | matplotlib__matplotlib-24026 | 15 min - 1 hour | ✅ | 297 | 18 | 0.0075 | ✅ | 131 | 17 | 0.0052 |
| 26 | django__django-13363 | <15 min fix | ✅ | 125 | 22 | 0.0055 | ✅ | 72 | 16 | 0.0039 |
| 27 | django__django-15467 | <15 min fix | ✅ | 215 | 28 | 0.0066 | ✅ | 86 | 16 | 0.0035 |
| 28 | django__django-16429 | <15 min fix | ✅ | 166 | 16 | 0.0029 | ✅ | 20 | 6 | 0.0012 |
| 29 | scikit-learn__scikit-learn-14087 | 15 min - 1 hour | ✅ | 243 | 22 | 0.0103 | ✅ | 418 | 39 | 0.0224 |
| 30 | django__django-13807 | <15 min fix | ✅ | 204 | 22 | 0.0059 | ✅ | 1093 | 29 | 0.0091 |
| 31 | sphinx-doc__sphinx-10323 | <15 min fix | ✅ | 325 | 42 | 0.0160 | ✅ | 115 | 17 | 0.0064 |
| 32 | pydata__xarray-4094 | <15 min fix | ✅ | 200 | 21 | 0.0065 | ✅ | 213 | 24 | 0.0088 |
| 33 | sphinx-doc__sphinx-8595 | <15 min fix | ✅ | 207 | 37 | 0.0101 | ✅ | 102 | 21 | 0.0057 |
| 34 | astropy__astropy-13033 | 15 min - 1 hour | ✅ | 327 | 44 | 0.0200 | ✅ | 196 | 23 | 0.0073 |
| 35 | sphinx-doc__sphinx-9230 | <15 min fix | ✅ | 416 | 37 | 0.0126 | ✅ | 104 | 17 | 0.0057 |
| 36 | django__django-13568 | 15 min - 1 hour | ✅ | 141 | 15 | 0.0043 | ✅ | 124 | 23 | 0.0065 |
| 37 | sympy__sympy-13372 | <15 min fix | ✅ | 161 | 16 | 0.0033 | ✅ | 211 | 24 | 0.0097 |
| 38 | django__django-14559 | 15 min - 1 hour | ✅ | 108 | 21 | 0.0043 | ✅ | 44 | 13 | 0.0025 |
| 39 | django__django-10999 | <15 min fix | ✅ | 283 | 27 | 0.0154 | ❌ | 145 | 16 | 0.0058 |
| 40 | django__django-15569 | <15 min fix | ✅ | 162 | 22 | 0.0058 | ✅ | 94 | 13 | 0.0034 |
| 41 | django__django-13033 | 15 min - 1 hour | ✅ | 394 | 51 | 0.0277 | ✅ | 186 | 25 | 0.0102 |
| 42 | sphinx-doc__sphinx-8593 | 15 min - 1 hour | ✅ | 947 | 100 | 0.0621 | ✅ | 190 | 32 | 0.0146 |
| 43 | django__django-12965 | 15 min - 1 hour | ✅ | 604 | 60 | 0.0302 | ✅ | 227 | 27 | 0.0132 |
| 44 | sympy__sympy-23262 | 15 min - 1 hour | ✅ | 133 | 19 | 0.0040 | ✅ | 60 | 15 | 0.0048 |
| 45 | django__django-15916 | 15 min - 1 hour | ✅ | 552 | 58 | 0.0311 | ✅ | 143 | 21 | 0.0077 |
| 46 | django__django-15503 | 1-4 hours | ✅ | 258 | 34 | 0.0153 | ✅ | 162 | 25 | 0.0093 |
| 47 | pydata__xarray-6721 | 15 min - 1 hour | ✅ | 523 | 39 | 0.0186 | ✅ | 266 | 29 | 0.0163 |
| 48 | astropy__astropy-14995 | <15 min fix | ✅ | 87 | 12 | 0.0041 | ✅ | 50 | 8 | 0.0022 |
| 49 | django__django-11490 | <15 min fix | ✅ | 711 | 44 | 0.0165 | ✅ | 249 | 46 | 0.0185 |
| 50 | matplotlib__matplotlib-24570 | <15 min fix | ✅ | 159 | 15 | 0.0052 | ✅ | 68 | 9 | 0.0029 |
| 51 | django__django-13810 | 15 min - 1 hour | ✅ | 332 | 35 | 0.0185 | ✅ | 177 | 18 | 0.0081 |
| 52 | sympy__sympy-12419 | 15 min - 1 hour | ✅ | 941 | 59 | 0.0322 | ✅ | 433 | 48 | 0.0214 |
| 53 | django__django-14765 | <15 min fix | ✅ | 80 | 12 | 0.0023 | ✅ | 56 | 16 | 0.0032 |
| 54 | scikit-learn__scikit-learn-13328 | <15 min fix | ✅ | 64 | 10 | 0.0025 | ✅ | 38 | 5 | 0.0016 |
| 55 | django__django-11815 | 15 min - 1 hour | ✅ | 590 | 35 | 0.0307 | ❌ | 124 | 21 | 0.0064 |
| 56 | sympy__sympy-15599 | 15 min - 1 hour | ✅ | 1017 | 45 | 0.0243 | ✅ | 790 | 41 | 0.0304 |
| 57 | django__django-13109 | <15 min fix | ✅ | 75 | 15 | 0.0024 | ✅ | 59 | 12 | 0.0026 |
| 58 | django__django-11119 | <15 min fix | ✅ | 85 | 15 | 0.0035 | ✅ | 47 | 11 | 0.0021 |
| 59 | pytest-dev__pytest-7236 | 15 min - 1 hour | ✅ | 234 | 21 | 0.0098 | ✅ | 121 | 14 | 0.0051 |
| 60 | astropy__astropy-13977 | 15 min - 1 hour | ✅ | 590 | 58 | 0.0286 | ✅ | 290 | 36 | 0.0182 |
| 61 | django__django-14493 | <15 min fix | ✅ | 128 | 20 | 0.0048 | ❌ | 46 | 9 | 0.0021 |
| 62 | sympy__sympy-19637 | <15 min fix | ✅ | 223 | 26 | 0.0091 | ✅ | 52 | 10 | 0.0027 |
| 63 | django__django-13551 | <15 min fix | ✅ | 168 | 21 | 0.0069 | ❌ | 58 | 7 | 0.0019 |
| 64 | scikit-learn__scikit-learn-14710 | 15 min - 1 hour | ❌ | 1214 | 31 | 0.0092 | ✅ | 154 | 13 | 0.0038 |
| 65 | matplotlib__matplotlib-20676 | <15 min fix | ✅ | 286 | 29 | 0.0132 | ✅ | 147 | 19 | 0.0092 |
| 66 | django__django-11734 | 15 min - 1 hour | ❌ | 854 | 100 | 0.0903 | ❌ | 382 | 55 | 0.0313 |
| 67 | django__django-16256 | 15 min - 1 hour | ❌ | 503 | 54 | 0.0277 | ❌ | 169 | 28 | 0.0120 |
| 68 | scikit-learn__scikit-learn-13439 | <15 min fix | ✅ | 126 | 20 | 0.0052 | ✅ | 30 | 6 | 0.0012 |
| 69 | django__django-15741 | <15 min fix | ✅ | 206 | 30 | 0.0092 | ✅ | 79 | 17 | 0.0040 |
| 70 | scikit-learn__scikit-learn-12973 | 15 min - 1 hour | ✅ | 213 | 18 | 0.0048 | ❌ | 33 | 7 | 0.0016 |
| 71 | matplotlib__matplotlib-25479 | <15 min fix | ✅ | 467 | 50 | 0.0260 | ✅ | 247 | 39 | 0.0179 |
| 72 | sphinx-doc__sphinx-9229 | 1-4 hours | ✅ | 1240 | 91 | 0.0659 | ✅ | 398 | 41 | 0.0208 |
| 73 | sympy__sympy-22914 | 15 min - 1 hour | ✅ | 98 | 18 | 0.0033 | ✅ | 84 | 18 | 0.0044 |
| 74 | sympy__sympy-24443 | 15 min - 1 hour | ✅ | 415 | 35 | 0.0187 | ✅ | 343 | 28 | 0.0156 |
| 75 | psf__requests-2931 | 15 min - 1 hour | ❌ | 857 | 48 | 0.0169 | ❌ | 599 | 11 | 0.0025 |
| 76 | sphinx-doc__sphinx-8475 | <15 min fix | ❌ | 187 | 29 | 0.0102 | ❌ | 54 | 14 | 0.0027 |
| 77 | sphinx-doc__sphinx-7454 | <15 min fix | ✅ | 366 | 68 | 0.0280 | ✅ | 72 | 17 | 0.0046 |
| 78 | sphinx-doc__sphinx-9367 | <15 min fix | ✅ | 104 | 15 | 0.0039 | ✅ | 41 | 8 | 0.0017 |
| 79 | sympy__sympy-13877 | 15 min - 1 hour | ✅ | 807 | 64 | 0.0464 | ✅ | 341 | 47 | 0.0327 |
| 80 | django__django-15957 | 1-4 hours | ✅ | 420 | 62 | 0.0308 | ✅ | 499 | 55 | 0.0302 |
| 81 | sympy__sympy-22714 | <15 min fix | ✅ | 172 | 19 | 0.0048 | ✅ | 134 | 14 | 0.0071 |
| 82 | astropy__astropy-13579 | 1-4 hours | ✅ | 537 | 45 | 0.0345 | ✅ | 273 | 20 | 0.0119 |
| 83 | pydata__xarray-3095 | 15 min - 1 hour | ✅ | 588 | 40 | 0.0144 | ✅ | 154 | 21 | 0.0071 |
| 84 | sphinx-doc__sphinx-7985 | 15 min - 1 hour | ✅ | 294 | 44 | 0.0213 | ✅ | 132 | 26 | 0.0097 |
| 85 | pytest-dev__pytest-7571 | 15 min - 1 hour | ✅ | 571 | 46 | 0.0229 | ✅ | 106 | 23 | 0.0082 |
| 86 | pydata__xarray-6938 | 15 min - 1 hour | ✅ | 1117 | 87 | 0.0484 | ✅ | 678 | 44 | 0.0184 |
| 87 | sympy__sympy-21930 | 15 min - 1 hour | ✅ | 178 | 34 | 0.0100 | ✅ | 299 | 37 | 0.0202 |
| 88 | sympy__sympy-19783 | 15 min - 1 hour | ✅ | 381 | 20 | 0.0052 | ✅ | 136 | 24 | 0.0076 |
| 89 | django__django-14608 | <15 min fix | ✅ | 287 | 41 | 0.0177 | ✅ | 117 | 28 | 0.0072 |
| 90 | sympy__sympy-12481 | <15 min fix | ✅ | 331 | 29 | 0.0159 | ✅ | 90 | 13 | 0.0031 |
| 91 | matplotlib__matplotlib-14623 | 15 min - 1 hour | ✅ | 325 | 29 | 0.0097 | ✅ | 202 | 30 | 0.0139 |
| 92 | scikit-learn__scikit-learn-10297 | 15 min - 1 hour | ✅ | 74 | 13 | 0.0030 | ✅ | 56 | 16 | 0.0037 |
| 93 | astropy__astropy-7336 | <15 min fix | ✅ | 132 | 22 | 0.0054 | ✅ | 29 | 8 | 0.0017 |
| 94 | sympy__sympy-14976 | 15 min - 1 hour | ✅ | 387 | 47 | 0.0184 | ✅ | 85 | 12 | 0.0035 |
| 95 | django__django-16560 | 1-4 hours | ✅ | 291 | 44 | 0.0219 | ✅ | 306 | 64 | 0.0281 |
| 96 | django__django-16631 | 1-4 hours | ✅ | 189 | 34 | 0.0115 | ✅ | 247 | 24 | 0.0147 |
| 97 | django__django-12125 | <15 min fix | ✅ | 1205 | 98 | 0.0699 | ✅ | 266 | 42 | 0.0191 |
| 98 | django__django-11848 | 15 min - 1 hour | ✅ | 191 | 23 | 0.0103 | ❌ | 72 | 12 | 0.0034 |
| 99 | django__django-16899 | <15 min fix | ✅ | 133 | 26 | 0.0047 | ✅ | 71 | 16 | 0.0035 |

✅ resolved, ❌ patch applied but tests fail (or patch failed to apply), ∅ empty patch.

Steps and tokens come from the local metering proxy each agent talked to. Cost uses the GMI prices in `run_config.json`. Wall time is the agent only (not image pull or scoring).
