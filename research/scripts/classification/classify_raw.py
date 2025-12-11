"""
classify_raw.py

LLM-only vulnerability classification for Solidity smart contracts
(no RAG / knowledge store).

This script:
    • Accepts either:
        - a contract ID (e.g., reentrancy_000), OR
        - a path to a .sol file or directory.
    • Resolves the actual Solidity file to analyze:
        - If `target` is a path:
            • directory → uses <dir>/malicious.sol
            • file      → uses that file directly
        - If `target` is NOT a path:
            • looks for data/synthetic/*/<target>/malicious.sol
    • Numbers the lines to help the model approximate "lines" indices.
    • Fills the prompts/classify_raw.txt template with:
        - {contract}    → numbered Solidity source
        - {contract_id} → identifier for JSON "id" field
    • Calls an OpenAI chat model in JSON mode (response_format=json_object).
    • Produces a single JSON object constrained to 10 attack categories:
        access_control, arithmetic, denial_of_service, front_running,
        initialization, reentrancy, signature_verification,
        unchecked_return_value, unencrypted_private_data,
        unprotected_self_destruct
    • Validates the JSON and writes the result to disk.

Output:
    • If the underlying target is a directory (e.g., data/synthetic/reentrancy/reentrancy_000),
      it expects malicious.sol inside and writes:
          data/synthetic/reentrancy/reentrancy_000/malicious_raw.json
    • If the underlying target is a .sol file, it writes <stem>_raw.json
      in the same directory.

Examples:
    # Use a synthetic contract ID (auto-resolves under data/synthetic/*/)
    uv run python scripts/classification/classify_raw.py \
        reentrancy_000 \
        --model gpt-5.1

    # Or call directly on a directory
    uv run python scripts/classification/classify_raw.py \
        data/synthetic/reentrancy/reentrancy_000 \
        --model gpt-5.1

    # Or call directly on a .sol file
    uv run python scripts/classification/classify_raw.py \
        path/to/SomeContract.sol \
        --model gpt-5.1
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------
# Project root and constants
# ---------------------------------------------------------------------

RELATIVE_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_ROOT = RELATIVE_ROOT / "data" / "synthetic"
PROMPT_PATH = RELATIVE_ROOT / "prompts" / "classify_raw.txt"

ALLOWED_ATTACK_TYPES = [
    "access_control",
    "arithmetic",
    "denial_of_service",
    "front_running",
    "initialization",
    "reentrancy",
    "signature_verification",
    "unchecked_return_value",
    "unencrypted_private_data",
    "unprotected_self_destruct",
]

ALLOWED_SEVERITIES = ["low", "medium", "high"]

DEFAULT_MODEL = "gpt-4.1-mini"


# ---------------------------------------------------------------------
# File + path helpers
# ---------------------------------------------------------------------

def load_contract(path: Path) -> str:
    """
    Read contract and prefix each line with a line number.

    Example:
        1: pragma solidity ^0.8.20;
        2: contract Foo { ...
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    return "\n".join(f"{i + 1}: {line}" for i, line in enumerate(lines))


def load_prompt_template() -> str:
    """Load the classify_raw.txt prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def fill_prompt_template(
    template: str,
    contract_text: str,
    contract_id: str,
) -> str:
    """
    Fill classify_raw.txt template.

    Template must use:
        {contract}    → numbered Solidity source
        {contract_id} → identifier for JSON "id"
    """
    prompt = template.replace("{contract}", contract_text)
    prompt = prompt.replace("{contract_id}", contract_id)
    return prompt


def resolve_contract_target(target: str) -> Tuple[Path, str, Path]:
    """
    Resolve the user-provided target into:
        contract_path : Path to .sol file to analyze
        contract_id   : ID used in JSON "id" field
        out_path      : Where to write <...>_raw.json

    Resolution order:
        1) If `target` is an existing path:
            - directory → use <dir>/malicious.sol, output <dir>/malicious_raw.json
            - file      → use that file, output <dir>/<stem>_raw.json
        2) Else, treat `target` as a synthetic contract ID (e.g., reentrancy_000):
            - search under data/synthetic/*/<target>/malicious.sol
            - if exactly one match, use it
    """
    maybe_path = Path(target)

    # Case 1: user passed an actual path
    if maybe_path.exists():
        if maybe_path.is_dir():
            contract_path = maybe_path / "malicious.sol"
            if not contract_path.exists():
                raise FileNotFoundError(f"Expected malicious.sol in {maybe_path}, but not found.")
            contract_id = maybe_path.name
            out_path = maybe_path / "classify_raw.json"
            return contract_path, contract_id, out_path

        # It's a file
        contract_path = maybe_path
        if contract_path.suffix != ".sol":
            raise ValueError(f"Expected a .sol file, got: {contract_path}")
        contract_id = contract_path.stem
        out_path = contract_path.with_name(contract_path.stem + "_raw.json")
        return contract_path, contract_id, out_path

    # Case 2: treat `target` as an ID under data/synthetic/*/<id>
    matches = list(SYNTHETIC_ROOT.glob(f"*/{target}"))
    if not matches:
        raise FileNotFoundError(
            f"Could not resolve '{target}' as a path or synthetic ID. "
            f"Searched under {SYNTHETIC_ROOT}/*/{target}"
        )
    if len(matches) > 1:
        raise RuntimeError(
            f"Ambiguous synthetic ID '{target}': found multiple matches:\n"
            + "\n".join(f"  - {m}" for m in matches)
        )

    dir_path = matches[0]
    contract_path = dir_path / "malicious.sol"
    if not contract_path.exists():
        raise FileNotFoundError(f"Expected malicious.sol in {dir_path}, but not found.")

    contract_id = target
    out_path = dir_path / "classify_raw.json"
    return contract_path, contract_id, out_path


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

def validate_output(data: Dict[str, Any], contract_id: str) -> Tuple[bool, List[str]]:
    """
    Validate the JSON output schema from the model.

    Rules adapted to your prompt:
        • id          must equal contract_id
        • solidity    must exist (value is not strictly enforced here)
        • attacks     may be:
            - a list of attack objects, or
            - null / None (treated as "no vulnerabilities")
        • each attack object:
            - type       in ALLOWED_ATTACK_TYPES
            - severity   in ALLOWED_SEVERITIES
            - lines      list[int]
            - description str
            - refs       MUST be None (null in JSON)
    """
    errors: List[str] = []

    if "id" not in data:
        errors.append("Missing top-level 'id'.")
    elif data["id"] != contract_id:
        errors.append(f"'id' mismatch: expected '{contract_id}', got '{data['id']}'.")

    if "solidity" not in data:
        errors.append("Missing top-level 'solidity'.")

    if "attacks" not in data:
        errors.append("Missing top-level 'attacks'.")

    attacks = data.get("attacks")

    # No vulnerabilities: accept [] or None
    if attacks is None or attacks == []:
        return (len(errors) == 0, errors)

    if not isinstance(attacks, list):
        errors.append("'attacks' must be a list or null.")
        return (False, errors)

    for i, attack in enumerate(attacks):
        if not isinstance(attack, dict):
            errors.append(f"Attack[{i}] is not an object.")
            continue

        t = attack.get("type")
        sev = attack.get("severity")
        lines = attack.get("lines")
        desc = attack.get("description")
        refs = attack.get("refs")

        if t not in ALLOWED_ATTACK_TYPES:
            errors.append(
                f"Attack[{i}].type '{t}' not in allowed types {ALLOWED_ATTACK_TYPES}"
            )

        if sev not in ALLOWED_SEVERITIES:
            errors.append(
                f"Attack[{i}].severity '{sev}' not in {ALLOWED_SEVERITIES}"
            )

        if not isinstance(lines, list) or not all(isinstance(x, int) for x in lines):
            errors.append(f"Attack[{i}].lines must be a list of integers.")

        if not isinstance(desc, str):
            errors.append(f"Attack[{i}].description must be a string.")

        # NEW RULE: refs MUST be null / None
        if refs is not None:
            errors.append(
                f"Attack[{i}].refs must be null (None), got: {refs!r}"
            )

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------
# Core classification logic
# ---------------------------------------------------------------------

def classify_raw_contract(
    contract_path: Path,
    contract_id: str,
    model: str,
    out_path: Path,
) -> None:
    """
    Run LLM-only classification on a single contract.

    Steps:
        1. Load and line-number the contract.
        2. Load the classify_raw.txt prompt.
        3. Fill {contract} and {contract_id}.
        4. Call OpenAI chat completion in JSON mode.
        5. Validate and write <...>_raw.json.
    """
    # Load env and create client once per run
    load_dotenv(RELATIVE_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key)

    # 1) Contract text
    contract_text = load_contract(contract_path)

    # 2) Prompt template
    template = load_prompt_template()
    prompt = fill_prompt_template(
        template=template,
        contract_text=contract_text,
        contract_id=contract_id,
    )

    # 3) Call model with JSON output enforced
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict smart contract vulnerability classifier. "
                    "You must follow the prompt instructions exactly and output ONLY JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    raw_content = resp.choices[0].message.content

    # 4) Parse JSON
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Model output was not valid JSON. Error: {e}\nRaw content:\n{raw_content}"
        )

    # 5) Validate
    ok, errors = validate_output(data, contract_id)
    if not ok:
        print("WARNING: Output did not fully pass validation:")
        for err in errors:
            print("  -", err)

    # 6) Write to disk
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[classify_raw] Wrote RAW classification JSON to {out_path}")


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LLM-only vulnerability classification (no RAG). "
                    "Target can be a path OR a synthetic contract ID."
    )
    parser.add_argument(
        "target",
        type=str,
        help=(
            "Either:\n"
            "  • A Solidity contract ID (e.g., reentrancy_000), which will be "
            "resolved under data/synthetic/*/<id>/malicious.sol, OR\n"
            "  • A path to a directory containing malicious.sol, OR\n"
            "  • A path to a .sol file."
        ),
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL}).",
    )

    args = parser.parse_args()

    contract_path, contract_id, out_path = resolve_contract_target(args.target)

    classify_raw_contract(
        contract_path=contract_path,
        contract_id=contract_id,
        model=args.model,
        out_path=out_path,
    )


if __name__ == "__main__":
    main()
