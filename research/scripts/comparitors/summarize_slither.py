"""
summarize_slither.py

Updated for NEW folder structure:

    data/synthetic/<attack_type>/<attack_type_xxx>/
        malicious.sol
        safe.sol
        metadata.json
        slither.json              <-- INPUT (read)
        slither_normalized.json   <-- OUTPUT (write)

This script converts raw Slither JSON reports into compact,
normalized summaries used for ML evaluation and comparison
to LLM-generated vulnerability metadata.

Responsibilities:
    • Recursively locate all slither.json files across all attack folders
    • Extract detectors (impact: high/medium/low)
    • Map each detector → one of the 10 attack categories
    • Apply fallback classifier if unmapped
    • Write normalized results → slither_normalized.json
    • Skip files that already have normalized output

Does NOT:
    • run Slither
    • generate contracts
    • modify global metadata
    • write global slither directories

Usage:
    Bulk mode (recommended):
        uv run python scripts/comparitors/summarize_slither.py --all

    Single file:
        uv run python scripts/comparitors/summarize_slither.py \
            data/synthetic/access_control/access_control_000/slither.json
"""

import json
import argparse
from pathlib import Path

# ======================================================================
# CATEGORY MAP
# ======================================================================

CATEGORY_MAP = {

    # === 1. ACCESS CONTROL ============================================
    "arbitrary-send": "access_control",
    "arbitrary-send-erc20": "access_control",
    "arbitrary-send-eth": "access_control",
    "protected-vars": "access_control",
    "missing-zero-check": "access_control",
    "tx-origin": "access_control",
    "incorrect-modifier": "access_control",
    "events-access": "access_control",

    # === 2. ARITHMETIC ================================================
    "arithmetic": "arithmetic",
    "arithmetic-overflow": "arithmetic",
    "arithmetic-underflow": "arithmetic",
    "divide-before-multiply": "arithmetic",
    "incorrect-exp": "arithmetic",
    "too-many-digits": "arithmetic",

    # === 3. DENIAL OF SERVICE ========================================
    "calls-loop": "denial_of_service",
    "msg-value-loop": "denial_of_service",
    "costly-loop": "denial_of_service",
    "dead-code": "denial_of_service",
    "return-bomb": "denial_of_service",
    "rtlo": "denial_of_service",
    "cyclomatic-complexity": "denial_of_service",

    # === 4. FRONT RUNNING ============================================
    "timestamp": "front_running",
    "weak-prng": "front_running",
    "gelato-unprotected-randomness": "front_running",
    "incorrect-equality": "front_running",

    # === 5. INITIALIZATION ===========================================
    "uninitialized-state": "initialization",
    "uninitialized-local": "initialization",
    "uninitialized-storage": "initialization",
    "shadowing-state": "initialization",
    "shadowing-abstract": "initialization",
    "shadowing-local": "initialization",
    "multiple-constructors": "initialization",

    # === 6. reentrancy ===============================================
    "reentrancy": "reentrancy",
    "reentrancy-eth": "reentrancy",
    "reentrancy-no-eth": "reentrancy",
    "reentrancy-unlimited-gas": "reentrancy",
    "reentrancy-events": "reentrancy",
    "reentrancy-benign": "reentrancy",

    # === 7. SIGNATURE VERIFICATION ===================================
    "tainted-signature": "signature_verification",
    "encode-packed-collision": "signature_verification",
    "domain-separator-collision": "signature_verification",
    "ecdsa": "signature_verification",

    # === 8. UNCHECKED RETURN VALUE ====================================
    "unchecked-lowlevel": "unchecked_return_value",
    "unchecked-send": "unchecked_return_value",
    "unchecked-transfer": "unchecked_return_value",
    "unused-return": "unchecked_return_value",
    "low-level-calls": "unchecked_return_value",

    # === 9. UNENCRYPTED PRIVATE DATA =================================
    "public-mappings-nested": "unencrypted_private_data",
    "var-read-using-this": "unencrypted_private_data",

    # === 10. UNPROTECTED SELF-DESTRUCT ================================
    "suicidal": "unprotected_self_destruct",
    "controlled-delegatecall": "unprotected_self_destruct",
    "delegatecall-loop": "unprotected_self_destruct",
    "controlled-array-length": "unprotected_self_destruct",
}


# ======================================================================
# FALLBACK CLASSIFIER
# ======================================================================

def classify_detector(detector: str):
    name = detector.lower()

    # 1. ACCESS CONTROL
    if "access" in name or "arbitrary" in name or "auth" in name:
        return "access_control"

    # 2. ARITHMETIC
    if "overflow" in name or "underflow" in name or "arith" in name:
        return "arithmetic"

    # 3. DENIAL OF SERVICE
    if "loop" in name or "gas" in name or "denial" in name or "dos" in name:
        return "denial_of_service"

    # 4. FRONT-RUNNING
    if "timestamp" in name or "prng" in name or "random" in name or "front" in name:
        return "front_running"

    # 5. INITIALIZATION
    if "uninit" in name or "shadow" in name or "constructor" in name:
        return "initialization"

    # 6. reentrancy (YOUR SPELLING)
    if "reentranc" in name:
        return "reentrancy"

    # 7. SIGNATURE VERIFICATION
    if "signature" in name or "ecdsa" in name or "collision" in name:
        return "signature_verification"

    # 8. UNCHECKED RETURN VALUE
    if "unchecked" in name or "unused-return" in name or "lowlevel" in name:
        return "unchecked_return_value"

    # 9. UNENCRYPTED PRIVATE DATA
    if "private" in name or "leak" in name:
        return "unencrypted_private_data"

    # 10. UNPROTECTED SELF-DESTRUCT
    if "selfdestruct" in name or "suicide" in name:
        return "unprotected_self_destruct"

    return None




def get_category(detector: str):
    explicit = CATEGORY_MAP.get(detector)
    if explicit:
        return explicit

    fallback = classify_detector(detector)
    if fallback:
        print(f"[INFO] Fallback classified '{detector}' → '{fallback}'")
        return fallback

    print(f"[WARNING] Could not classify '{detector}'")
    return None

# ======================================================================
# SUMMARY EXTRACTION
# ======================================================================

def extract_summary(raw_path: Path):
    data = json.loads(raw_path.read_text())
    detectors = data.get("results", {}).get("detectors", [])
    summary = []

    for d in detectors:
        impact = d.get("impact", "").lower()
        if impact not in ["high", "medium", "low"]:
            continue

        detector = d.get("check", "")
        category = get_category(detector)

        lines = []
        for el in d.get("elements", []):
            src = el.get("source_mapping", {})
            if "lines" in src:
                lines.extend(src["lines"])

        summary.append({
            "slither_check": detector,
            "category": category,
            "severity": impact,
            "confidence": d.get("confidence", ""),
            "description": d.get("description", "").strip(),
            "lines": sorted(set(lines)),
        })

    return {
        "file": str(raw_path),
        "vulnerabilities": summary,
    }

# ======================================================================
# BULK MODE
# ======================================================================

def run_bulk():
    """
    Find every slither.json inside data/synthetic/**/**/
    """
    all_raw = sorted(Path("data/synthetic").glob("*/*/slither.json"))
    print(f"[INFO] Found {len(all_raw)} raw Slither reports")

    for raw in all_raw:
        norm_path = raw.parent / "slither_normalized.json"

        if norm_path.exists():
            print(f"[SKIP] {norm_path} already exists")
            continue

        summary = extract_summary(raw)
        norm_path.write_text(json.dumps(summary, indent=2))
        print(f"[OK] Normalized {raw} → {norm_path}")

    print("[DONE] Bulk normalization complete")

# ======================================================================
# CLI
# ======================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="Single slither.json path")
    parser.add_argument("--all", action="store_true", help="Process all files")
    args = parser.parse_args()

    if args.all:
        return run_bulk()

    if not args.file:
        raise ValueError("Provide a file or use --all")

    raw_path = Path(args.file)
    norm_path = raw_path.parent / "slither_normalized.json"

    summary = extract_summary(raw_path)
    norm_path.write_text(json.dumps(summary, indent=2))

    print(f"[OK] Normalized {raw_path} → {norm_path}")


if __name__ == "__main__":
    main()
