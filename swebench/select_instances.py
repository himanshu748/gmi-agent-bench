"""Fixed, seeded random order over SWE-bench Verified (500 instances).

Instances are run in this order, so any prefix (first 5 = pilot, first N = main run)
is itself a uniform random sample of the full Verified set.
"""
import random
from pathlib import Path

from datasets import load_dataset

SEED = 20261126
ds = load_dataset("SWE-bench/SWE-bench_Verified", split="test")
ids = sorted(ds["instance_id"])
random.Random(SEED).shuffle(ids)
Path(__file__).with_name("instances.txt").write_text(
    f"# SWE-bench Verified, random.Random({SEED}).shuffle(sorted(ids)); run in this order\n" + "\n".join(ids) + "\n")
print(ids[:10])
