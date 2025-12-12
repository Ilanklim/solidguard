"""
contract_classifier.py

Provides two simple functions for frontend use:

1. classify_raw_contract_text(contract_text: str, model="gpt-5.1")
2. classify_rag_contract_text(contract_text: str, model="gpt-5.1", k=5)

Both return a Python dict containing the parsed JSON classification.

This module:
    ✓ Does NOT write files
    ✓ Does NOT require synthetic folders
    ✓ Works directly on user-submitted smart contracts
    ✓ Uses your existing RAW + RAG prompt logic
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from backend.retrieve_embeddings import KnowledgeStore

# Load environment
LOCAL_ROOT = Path(__file__).resolve().parents[0]
load_dotenv(LOCAL_ROOT / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing in environment!")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------
# Constants
# ---------------------------------------------
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

RAW_PROMPT = (LOCAL_ROOT / "prompts" / "classify_raw.txt").read_text(encoding="utf-8")
RAG_PROMPT = (LOCAL_ROOT / "prompts" / "classify_rag.txt").read_text(encoding="utf-8")

# For RAG retrieval
KS = KnowledgeStore(path=LOCAL_ROOT / "knowledge_store.jsonl")
KS.load()


# ---------------------------------------------
# Utilities
# ---------------------------------------------

def number_contract_lines(text: str) -> str:
    """Add line numbers to contract source."""
    return "\n".join(f"{i+1}: {line}" for i, line in enumerate(text.splitlines()))


def enforce_json_completion(model: str, prompt: str) -> dict:
    """Send prompt → enforce JSON → return parsed dict."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "You are a strict smart-contract vulnerability classifier. Output ONLY JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    raw = resp.choices[0].message.content
    if raw is None:
        raise RuntimeError("LLM returned no content (None). Cannot parse JSON.")
    return json.loads(raw)


# ---------------------------------------------
# RAW CLASSIFIER FUNCTION
# ---------------------------------------------

def classify_raw_contract_text(contract_text: str, model: str = "gpt-5.1") -> dict:
    """
    Classify a smart contract WITHOUT RAG.

    Args:
        contract_text (str): Solidity contract
        model (str): OpenAI model name

    Returns:
        dict: JSON classification
    """
    numbered = number_contract_lines(contract_text)

    # Fill template
    prompt = (
        RAW_PROMPT
        .replace("{contract}", numbered)
        .replace("{contract_id}", "user_input_contract")
    )

    result = enforce_json_completion(model, prompt)

    # RAW classifier requires refs=None
    if result.get("attacks"):
        for attack in result["attacks"]:
            attack["refs"] = None

    return result


# ---------------------------------------------
# RAG CLASSIFIER FUNCTION
# ---------------------------------------------

def classify_rag_contract_text(
    contract_text: str,
    model: str = "gpt-5.1",
    k: int = 5,
) -> dict:
    """
    Classify a smart contract WITH RAG retrieval.

    Args:
        contract_text (str): Solidity source code
        model (str): OpenAI model name
        k (int): Number of RAG documents to retrieve

    Returns:
        dict: JSON classification
    """
    numbered = number_contract_lines(contract_text)

    # Retrieve docs
    hits = KS.retrieve(numbered, k=k)
    docs_block = []
    rag_refs = []

    for i, h in enumerate(hits, start=1):
        docs_block.append(
            f"[DOC {i} | category={h['category']} | source={h['source']}]\\n{h['text']}"
        )
        filename = Path(h["source"]).name
        idx = h.get("chunk_index", 0)
        rag_refs.append(f"{h['category']}::{filename}::chunk_{idx}")

    joined_docs = "\n\n".join(docs_block) if docs_block else "No RAG documents retrieved."

    # Fill template
    prompt = (
        RAG_PROMPT
        .replace("{retrieved_docs}", joined_docs)
        .replace("{contract}", numbered)
        .replace("{contract_id}", "user_input_contract")
    )

    result = enforce_json_completion(model, prompt)

    # Append RAG refs to each attack
    if result.get("attacks"):
        for attack in result["attacks"]:
            attack["refs"] = rag_refs.copy()

    return result
