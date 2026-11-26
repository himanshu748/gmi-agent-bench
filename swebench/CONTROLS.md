# Scorer controls (run 2026-11-26 on this box)

Official `swebench` 5.0.2 harness, local Docker, instance `django__django-11740`:

| Prediction | Expected | Harness result |
| --- | --- | --- |
| Gold patch from the dataset | resolved | resolved (1/1 FAIL_TO_PASS, 109/109 PASS_TO_PASS) |
| No-op patch (`negative_control_noop.diff`: appends a comment to the file the gold patch edits) | unresolved | unresolved |

Reproduce: `python -m swebench.harness.run_evaluation -d SWE-bench/SWE-bench_Verified -p <preds.json> --run_id ctl -i django__django-11740`.
