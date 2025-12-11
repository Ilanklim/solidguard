#!/usr/bin/env python3
"""
classify_all.py

Runs BOTH classify_raw.py and classify_rag.py
on EVERY contract folder under data/synthetic/*/*.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
print(f"ROOT IS {ROOT}")
SYN = ROOT / "data" / "synthetic"

RAW_SCRIPT = ROOT / "scripts" / "classification" / "classify_raw.py"
RAG_SCRIPT = ROOT / "scripts" / "classification" / "classify_rag.py"

MODEL = "gpt-5.1"


def run(cmd):
    print(" ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def main():
    for category in SYN.iterdir():
        if not category.is_dir():
            continue

        for contract_dir in category.iterdir():
            if not contract_dir.is_dir():
                continue

            print(f"\n=== CLASSIFYING {contract_dir.name} ===")

            # RAW
            run([
                "uv", "run", "python", str(RAW_SCRIPT),
                str(contract_dir),
                "--model", MODEL
            ])

            # RAG
            run([
                "uv", "run", "python", str(RAG_SCRIPT),
                str(contract_dir),
                "--model", MODEL
            ])


if __name__ == "__main__":
    main()
