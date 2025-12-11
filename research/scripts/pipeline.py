"""
pipeline.py

Full orchestration for synthetic smart contract dataset.

Supports the following steps:
    1. generate_contracts.py
    2. run_slither.py
    3. summarize_slither.py
    4. classify_raw.py
    5. classify_rag.py

Typical usage:

    # Full generation → slither → summarize
    uv run python scripts/pipeline.py --all

    # Full end-to-end including classification
    uv run python scripts/pipeline.py --all-full

    # Only classification
    uv run python scripts/pipeline.py --classify-all
"""

import argparse
import subprocess
import sys
from pathlib import Path


# ======================================================================
# Helper
# ======================================================================
def run_script(path: str, args: list[str]):
    cmd = ["uv", "run", "python", path] + args
    print(f"\n[PIPELINE] Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"[ERROR] Step failed → {path}")
        sys.exit(result.returncode)


# ======================================================================
# Script paths
# ======================================================================
SCRIPTS_DIR = Path("scripts")

GEN_SCRIPT       = SCRIPTS_DIR / "generation"      / "generate_contracts.py"
SLITHER_SCRIPT   = SCRIPTS_DIR / "comparitors"     / "run_slither.py"
SUMMARY_SCRIPT   = SCRIPTS_DIR / "comparitors"     / "summarize_slither.py"
RAW_CLASS_SCRIPT = SCRIPTS_DIR / "classification"  / "classify_raw.py"
RAG_CLASS_SCRIPT = SCRIPTS_DIR / "classification"  / "classify_rag.py"

# Validate existence
for script in (GEN_SCRIPT, SLITHER_SCRIPT, SUMMARY_SCRIPT,
               RAW_CLASS_SCRIPT, RAG_CLASS_SCRIPT):
    if not script.exists():
        print(f"[ERROR] Missing script: {script}")
        sys.exit(1)


# ======================================================================
# Main
# ======================================================================
def main():
    parser = argparse.ArgumentParser()

    # generation arguments
    parser.add_argument("--num", type=int, default=10,
                        help="How many contract pairs to generate")

    parser.add_argument("--seed", type=int, default=4940,
                        help="Random seed")

    parser.add_argument("--model", type=str, default="gpt-4.1",
                        help="Which LLM to use for generation")

    # pipeline flags
    parser.add_argument("--generate",      action="store_true")
    parser.add_argument("--slither",       action="store_true")
    parser.add_argument("--summarize",     action="store_true")

    parser.add_argument("--classify-raw",  action="store_true",
                        help="Run classify_raw.py on all synthetic contracts")

    parser.add_argument("--classify-rag",  action="store_true",
                        help="Run classify_rag.py on all synthetic contracts")

    parser.add_argument("--classify-all",  action="store_true",
                        help="Run BOTH raw + rag classification")

    parser.add_argument("--all",       action="store_true",
                        help="Run: generate → slither → summarize")

    parser.add_argument("--all-full", action="store_true",
                        help="Run EVERYTHING: generate → slither → summarize → classify_raw → classify_rag")

    args = parser.parse_args()

    allowed_models = {"gpt-4.1-mini", "gpt-4.1", "gpt-5.1"}
    if args.model not in allowed_models:
        print(f"[ERROR] Invalid model {args.model}")
        sys.exit(1)

    model_arg = ["--model", args.model]

    # ------------------------------------------------------------------
    # FULL PIPELINE WITHOUT CLASSIFICATION
    # ------------------------------------------------------------------
    if args.all:
        run_script(str(GEN_SCRIPT),
                   ["--num_contracts", str(args.num),
                    "--seed", str(args.seed)] + model_arg)
        run_script(str(SLITHER_SCRIPT), [])
        run_script(str(SUMMARY_SCRIPT), ["--all"])
        print("\n[PIPELINE] Step (ALL) COMPLETE ✔\n")
        return

    # ------------------------------------------------------------------
    # FULL PIPELINE WITH CLASSIFICATION
    # ------------------------------------------------------------------
    if args.all_full:
        run_script(str(GEN_SCRIPT),
                   ["--num_contracts", str(args.num),
                    "--seed", str(args.seed)] + model_arg)
        run_script(str(SLITHER_SCRIPT), [])
        run_script(str(SUMMARY_SCRIPT), ["--all"])

        # run classification on all contracts
        run_script(str(RAW_CLASS_SCRIPT), ["--all"])
        run_script(str(RAG_CLASS_SCRIPT), ["--all"])

        print("\n[PIPELINE] FULL END-TO-END COMPLETE ✔\n")
        return

    # ------------------------------------------------------------------
    # INDIVIDUAL STEPS
    # ------------------------------------------------------------------
    if args.generate:
        run_script(str(GEN_SCRIPT),
                   ["--num_contracts", str(args.num),
                    "--seed", str(args.seed)] + model_arg)

    if args.slither:
        run_script(str(SLITHER_SCRIPT), [])

    if args.summarize:
        run_script(str(SUMMARY_SCRIPT), ["--all"])

    # ------------------------------------------------------------------
    # Classification only
    # ------------------------------------------------------------------
    if args.classify_raw:
        run_script(str(RAW_CLASS_SCRIPT), ["--all"])

    if args.classify_rag:
        run_script(str(RAG_CLASS_SCRIPT), ["--all"])

    if args.classify_all:
        run_script(str(RAW_CLASS_SCRIPT), ["--all"])
        run_script(str(RAG_CLASS_SCRIPT), ["--all"])

    # ------------------------------------------------------------------
    # No flags → show help
    # ------------------------------------------------------------------
    if not (args.generate or args.slither or args.summarize or
            args.classify_raw or args.classify_rag or
            args.classify_all or args.all or args.all_full):

        parser.print_help()


if __name__ == "__main__":
    main()