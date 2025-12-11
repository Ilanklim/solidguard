"""
generate_contracts.py

PURE CONTRACT GENERATION ONLY

Creates Solidity contract pairs:

    data/synthetic/<attack>/<attack_xxx>/malicious.sol
    data/synthetic/<attack>/<attack_xxx>/safe.sol

This script ONLY:
    • Selects next attack type (round-robin by count)
    • Generates malicious + safe contracts via OpenAI
    • Creates per-contract folders
    • Writes malicious.sol and safe.sol

This script DOES NOT:
    • Create metadata.json
    • Create global metadata
    • Create slither.json or slither_normalized.json
    • Run Slither or any analysis
    • Save any JSON outputs

Usage:
    uv run python scripts/generation/generate_contracts.py \
        --num_contracts 10 \
        --model gpt-5.1
"""


import argparse
import random
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# DIRECTORIES

BASE_DIR = Path("data/synthetic")
LOG_FILE = BASE_DIR / "generation.log"

PROMPT_PATH = Path("prompts/generate_contracts.txt")
PROMPT_TEMPLATE = PROMPT_PATH.read_text()

# ATTACK CATEGORIES
ATTACK_TYPES = [
    "access_control",
    "arithmetic",
    "denial_of_service",
    "front_running",
    "initialization",
    "reentrancy",
    "signature_verification",
    "unchecked_return_value",
    "unencrypted_private_data",
    "unprotected_self_destruct"
]

ALLOWED_MODELS = ["gpt-4.1-mini", "gpt-4.1", "gpt-5.1"]


# LOG HELPER
def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


# COUNT HELPERS
def count_existing_for_attack(attack_type: str) -> int:
    folder = BASE_DIR / attack_type
    if not folder.exists():
        return 0
    return sum(1 for x in folder.iterdir() if x.is_dir())


def get_next_attack_type() -> str:
    counts = {a: count_existing_for_attack(a) for a in ATTACK_TYPES}
    return min(counts, key=lambda a: counts[a])


def get_next_local_index(attack_type: str) -> int:
    folder = BASE_DIR / attack_type
    if not folder.exists():
        return 0

    max_idx = -1
    for child in folder.iterdir():
        if child.is_dir() and child.name.startswith(attack_type):
            try:
                idx = int(child.name.split("_")[-1])
                max_idx = max(max_idx, idx)
            except:
                pass

    return max_idx + 1


# PARSE LLM OUTPUT
def parse_llm_output(raw_output: str):
    """
    Extract:
        metadata_json, malicious contract text, safe contract text
    but ignore metadata entirely (we do not save it).
    """
    try:
        # Extract JSON blob
        start = raw_output.find("{")
        if start == -1:
            log("[ERROR] No JSON metadata found.")
            return None, None

        brace_count = 0
        end = None

        for i, ch in enumerate(raw_output[start:], start):
            if ch == "{":
                brace_count += 1
            elif ch == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break

        if end is None:
            log("[ERROR] JSON block not closed.")
            return None, None

        # Extract Solidity code
        remainder = raw_output[end:].strip()
        parts = remainder.split("// SAFE CONTRACT")
        if len(parts) < 2:
            log("[ERROR] SAFE CONTRACT delimiter missing.")
            return None, None

        mal = parts[0].replace("// MALICIOUS CONTRACT", "").strip()
        safe = parts[1].strip()

        return mal, safe

    except Exception as e:
        log(f"[PARSE ERROR] {e}")
        return None, None

# GENERATE ONE CONTRACT PAIR
def generate_one(attack_type: str, model: str):
    local_idx = get_next_local_index(attack_type)
    contract_id = f"{attack_type}_{local_idx:03d}"

    log(f"[GEN] {contract_id} ({attack_type}) using {model}")

    prompt = PROMPT_TEMPLATE.format(
        attack_type=attack_type,
        contract_id=contract_id
    )

    # Call OpenAI Responses API
    response = client.responses.create(
        model=model,
        input=prompt
    )
    raw_output = response.output_text

    malicious, safe = parse_llm_output(raw_output)

    if malicious is None or safe is None:
        log(f"[retry] Failed → retrying {contract_id}")
        return generate_one(attack_type, model)

    # Folder path: data/synthetic/<attack>/<attack_000>
    folder = BASE_DIR / attack_type / contract_id
    folder.mkdir(parents=True, exist_ok=True)

    # Write contracts only!
    (folder / "malicious.sol").write_text(malicious)
    (folder / "safe.sol").write_text(safe)

    log(f"[OK] {contract_id} generated → contracts saved.")


# GENERATE MANY CONTRACTS
def generate_dataset(num_contracts: int, model: str):
    for _ in range(num_contracts):
        attack = get_next_attack_type()
        generate_one(attack, model)


# CLI
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_contracts", type=int, default=1)
    parser.add_argument("--seed", type=int, default=4940)
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()

    if args.model not in ALLOWED_MODELS:
        raise ValueError(f"Model must be one of: {ALLOWED_MODELS}")

    random.seed(args.seed)
    log("=== Generation Start ===")

    generate_dataset(args.num_contracts, args.model)

    log("=== Generation Complete ===")


if __name__ == "__main__":
    main()