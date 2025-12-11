"""
run_slither.py

Updated for NEW folder structure:

    data/synthetic/<attack_type>/<attack_type_xxx>/
        malicious.sol
        safe.sol
        metadata.json
        slither.json                  <-- THIS SCRIPT WRITES HERE
        slither_normalized.json       <-- summarize_slither.py will write later

This script:

• Recursively finds ALL malicious.sol files across all attack folders
• Runs Slither on each malicious contract
• Writes raw Slither detector JSON → slither.json inside the contract folder
• Does NOT:
      - generate contracts
      - summarize Slither results
      - modify global metadata

Use this script whenever:
    • Slither version changes
    • Raw JSON reports are missing or corrupted
    • New contracts were generated
"""

import subprocess
from pathlib import Path

# Base directory
BASE_DIR = Path("data/synthetic")


def run_slither_on_file(sol_path: Path, out_path: Path):
    """
    Runs Slither on a single malicious.sol file and writes raw JSON results.
    """
    print(f"[Slither] {sol_path} → {out_path}")

    cmd = [
        "uv", "run", "slither",
        str(sol_path),
        "--json", str(out_path),
        "--json-types", "detectors",
        "--disable-color",
    ]

    result = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        print(f"[ERROR] Slither failed for {sol_path}")
        print(result.stderr[:300], "...\n")
    else:
        print(f"[OK] Created {out_path}")


def main():
    """
    Traverse NEW hierarchical structure and run Slither on all malicious.sol files.
    """
    malicious_files = list(BASE_DIR.glob("*/*/malicious.sol"))

    if not malicious_files:
        print("[WARN] No malicious.sol files found in data/synthetic/**/**/")
        return

    print(f"[INFO] Running Slither on {len(malicious_files)} malicious contracts...\n")

    for sol_path in malicious_files:
        contract_folder = sol_path.parent
        out_path = contract_folder / "slither.json"
        run_slither_on_file(sol_path, out_path)

    print("\n[DONE] Slither analysis complete for all malicious contracts.")


if __name__ == "__main__":
    main()
