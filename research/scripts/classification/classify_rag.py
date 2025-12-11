"""
classify_rag.py

RAG-based vulnerability classifier for Solidity smart contracts.

This script:
    • Loads a Solidity contract (file or a folder containing malicious.sol)
    • Embeds the contract and performs vector search over knowledge_store.jsonl
    • Retrieves the top-k most relevant RAG_docs
    • Fills the classify_rag.txt prompt with retrieved docs + contract source
    • Calls an OpenAI chat model in JSON mode
    • Produces a single JSON object constrained to 10 attack categories:
        access_control, arithmetic, denial_of_service, front_running,
        initialization, reentrancy, signature_verification,
        unchecked_return_value, unencrypted_private_data,
        unprotected_self_destruct
    • Validates the JSON and writes the result to disk

Input:
    • If `target` is a .sol file, that file is analyzed and output goes to
      data/llm/rag/
    • If `target` is a directory containing malicious.sol, that file is analyzed
      and output is written to the same directory as malicious.json

This script does NOT run Slither/Almanax or compute metrics. It is designed
to test how RAG retrieval affects LLM vulnerability classification and to
generate standardized JSON labels for later evaluation.

Example usage: 

python3 scripts/classification/classify_rag.py \
  data/synthetic/reentrancy/reentrancy_000 \
  --model gpt-5.1 \
  --k 6

"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sys
from dotenv import load_dotenv
from openai import OpenAI

# Allow importing retrieve_embeddings.KnowledgeStore
ROOT = Path(__file__).resolve().parents[3]
RELATIVE_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(RELATIVE_ROOT / "scripts" / "embeddings"))
from retrieve_embeddings import KnowledgeStore


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
DEFAULT_K = 5
DEFAULT_STORE_PATH = ROOT / "knowledge_store.jsonl"
DEFAULT_PROMPT_PATH = RELATIVE_ROOT / "prompts"/ "classify_rag.txt"
DEFAULT_OUTDIR = RELATIVE_ROOT / "data" / "synthetic" 


# ----------------------------
# Helpers
# ----------------------------

def load_contract(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Add line numbers so the model can approximate "lines" indices
    return "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))



def build_retrieved_docs_block(hits: List[Dict[str, Any]]):
    """
    Build the RAG_docs block for the prompt and a list of reference IDs.

    For each retrieved chunk we try to use its 'id' field from the
    knowledge store (e.g. "access_control::swc_unprotected_ether_withdrawal.txt::chunk_3").
    If 'id' is missing, we reconstruct a stable identifier from:
        <category>::<filename>::chunk_<chunk_index>

    Returns:
        docs_block (str): formatted prompt block
        refs_list (list[str]): list of RAG chunk ids (one per hit)
    """
    parts: List[str] = []
    refs: List[str] = []

    for i, h in enumerate(hits, start=1):
        category = h.get("category", "unknown")
        source = h.get("source", "unknown")
        text = h.get("text", "")

        # Prefer explicit id from the knowledge store if present
        doc_id = h.get("id")
        if not doc_id:
            # Fallback: reconstruct an ID from category + filename + chunk_index
            filename = Path(source).name if source and source != "unknown" else "unknown"
            chunk_idx = h.get("chunk_index", 0)
            doc_id = f"{category}::{filename}::chunk_{chunk_idx}"

        parts.append(
            f"[DOC {i} | id={doc_id} | category={category} | source={source}]\n{text}"
        )

        # Always append the ref, even if duplicates occur across chunks
        refs.append(doc_id)

    docs_block = "\n\n".join(parts) if parts else "No RAG documents were retrieved."
    return docs_block, refs



def load_prompt_template(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8")


def fill_prompt_template(
            template: str,
            retrieved_docs: str,
            contract_text: str,
            contract_id: str,) -> str:
    prompt = template
    prompt = prompt.replace("{retrieved_docs}", retrieved_docs)
    prompt = prompt.replace("{contract}", contract_text)
    prompt = prompt.replace("{contract_id}", contract_id)
    return prompt


def validate_output(data: Dict[str, Any], contract_id: str) -> Tuple[bool, List[str]]:
    """Validate the JSON output schema from the model (RAG-friendly)."""
    errors: List[str] = []

    # ---- Top-level checks ----
    if "id" not in data:
        errors.append("Missing top-level 'id'.")
    elif data["id"] != contract_id:
        errors.append(f"'id' mismatch: expected '{contract_id}', got '{data['id']}'.")

    if "solidity" not in data:
        errors.append("Missing top-level 'solidity'.")

    if "attacks" not in data:
        errors.append("Missing top-level 'attacks'.")

    attacks = data.get("attacks")

    # Accept None for no vulnerabilities
    if attacks is None:
        return (len(errors) == 0, errors)

    if not isinstance(attacks, list):
        errors.append("'attacks' must be a list or null.")
        return (False, errors)

    # ---- Attack-level checks ----
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
            errors.append(f"Attack[{i}].type '{t}' not allowed.")

        if sev not in ALLOWED_SEVERITIES:
            errors.append(f"Attack[{i}].severity '{sev}' invalid.")

        if not isinstance(lines, list) or not all(isinstance(x, int) for x in lines):
            errors.append(f"Attack[{i}].lines must be a list of integers.")

        if not isinstance(desc, str):
            errors.append(f"Attack[{i}].description must be a string.")

        # NEW: refs can be ANY list[str] (RAG IDs)
        if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
            errors.append(f"Attack[{i}].refs must be a list of strings.")

    return (len(errors) == 0, errors)



# ----------------------------
# Main classification routine
# ----------------------------

def classify_with_rag(
    contract_path: Path,
    contract_id: str,
    model: str,
    k: int,
    store_path: Path,
    prompt_path: Path,
    outdir: Path,
) -> None:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key)

    # Load contract
    contract_text = load_contract(contract_path)

    # Load RAG store
    ks = KnowledgeStore(path=store_path)
    ks.load()

    # Retrieve docs
    hits = ks.retrieve(contract_text, k=k)
    retrieved_docs_block, rag_refs = build_retrieved_docs_block(hits)

    # Prepare prompt
    template = load_prompt_template(prompt_path)
    prompt = fill_prompt_template(
        template=template,
        retrieved_docs=retrieved_docs_block,
        contract_text=contract_text,
        contract_id=contract_id,
    )

    # Call model
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict smart contract vulnerability classifier. "
                    "Output ONLY JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    raw_content = resp.choices[0].message.content

    # Parse JSON
    try:
        data = json.loads(raw_content)

        # Inject RAG references
        if data.get("attacks"):
            for attack in data["attacks"]:
                attack["refs"] = list(rag_refs)
        else:
            data["attacks"] = None

    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Model output was not valid JSON. Error: {e}\nRaw content:\n{raw_content}"
        )

    # Validate output
    ok, errors = validate_output(data, contract_id)
    if not ok:
        print("WARNING: RAG output failed validation:")
        for err in errors:
            print("  -", err)

    # Write JSON
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "classify_rag.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote RAG classification JSON to {out_path}")



# ----------------------------
# CLI
# ----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LLM-based vulnerability classification with RAG context."
    )
    parser.add_argument(
        "target",
        type=str,
        help=(
            "Path to Solidity contract OR directory containing malicious.sol. "
            "If a directory is given, malicious.sol will be used and JSON "
            "will be written to that same directory."
        ),
    )
    parser.add_argument(
        "--contract-id",
        type=str,
        default=None,
        help="Contract ID to embed in JSON output. Defaults to contract filename stem.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=DEFAULT_K,
        help=f"Number of RAG docs to retrieve (default: {DEFAULT_K}).",
    )
    parser.add_argument(
        "--store-path",
        type=str,
        default=str(DEFAULT_STORE_PATH),
        help=f"Path to knowledge_store.jsonl (default: {DEFAULT_STORE_PATH}).",
    )
    parser.add_argument(
        "--prompt-path",
        type=str,
        default=str(DEFAULT_PROMPT_PATH),
        help=f"Path to classify_rag.txt (default: {DEFAULT_PROMPT_PATH}).",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
        help=(
            "Optional override for output directory. "
            "If omitted and target is a directory, JSON is written to that directory. "
            "If omitted and target is a file, JSON is written to data/llm/rag/."
        ),
    )

    args = parser.parse_args()

    target_path = Path(args.target)

    # Determine contract_path and default outdir
    if target_path.is_dir():
        contract_path = target_path / "malicious.sol"
        if not contract_path.exists():
            raise FileNotFoundError(f"Expected malicious.sol in {target_path}, but not found.")
        default_outdir = target_path
    else:
        contract_path = target_path
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract file not found: {contract_path}")
        default_outdir = DEFAULT_OUTDIR

    # Determine contract_id
    if args.contract_id:
        contract_id = args.contract_id
    else:
        if target_path.is_dir():
            # Use the folder name like "reentrancy_001"
            contract_id = target_path.name
        else:
            # Use the file name stem only when calling directly on a .sol file
            contract_id = contract_path.stem



    # Determine output directory
    if args.outdir is not None:
        outdir = Path(args.outdir)
    else:
        outdir = default_outdir

    classify_with_rag(
        contract_path=contract_path,
        contract_id=contract_id,
        model=args.model,
        k=args.k,
        store_path=Path(args.store_path),
        prompt_path=Path(args.prompt_path),
        outdir=outdir,
    )


if __name__ == "__main__":
    main()

