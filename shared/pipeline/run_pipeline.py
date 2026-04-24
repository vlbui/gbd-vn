"""Run all pipeline stages (00 -> 04) in order.

Invoke from repo root:
    python shared/pipeline/run_pipeline.py

Stages are loaded by module path rather than `from . import 00_setup`
because leading-digit module names aren't valid Python identifiers.
"""

import importlib


STAGES = [
    "shared.pipeline.00_setup",
    "shared.pipeline.01_load_clean",
    "shared.pipeline.02_metrics",
    "shared.pipeline.03_trends",
    "shared.pipeline.04_decomposition",
]


def main():
    for mod_path in STAGES:
        mod = importlib.import_module(mod_path)
        mod.run()
    print("\n=== PIPELINE COMPLETE ===")


if __name__ == "__main__":
    main()
