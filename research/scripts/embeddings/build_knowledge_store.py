#!/usr/bin/env python3
"""
build_knowledge_store.py

Builds knowledge_store.jsonl from structured RAG docs under RAG_docs/.

Assumptions about RAG_docs:
- Directory structure: RAG_docs/<category>/*.txt
  where <category> is one of the 10 canonical attack types, e.g.:
    - access_control
    - arithmetic
    - denial_of_service
    - front_running
    - initialization
    - reentrancy
    - signature_verification
    - unchecked_return_value
    - unencrypted_private_data
    - unprotected_self_destruct

- Each .txt file follows a structure like:

    Vulnerability Name: access_control
    Title: Unprotected Ether Withdrawal (AttackType: access_control)
    SWC: SWC-105
    CWE: CWE-284 ...

    Description
    -----------

    Key Patterns
    ------------

    Impact
    ------

    Remediation
    -----------

    References
    ----------

    Samples
    =======

    Example: foo.sol (vulnerable — access_control)
    ...
    ```solidity
    pragma solidity ^0.8.20;
    ...
    ```

- Explanation sections come BEFORE "Samples".
- Each example starts with a line "Example: ...".

Chunking strategy:
- Everything before the "Samples" heading is treated as explanation text:
    section_type = "explanation"
    → further chunked by paragraphs if very long.
- The "Samples" section is split into chunks by "Example:" headings:
    section_type = "example"
    → each example's description + code stays together.

Writes:
- knowledge_store.jsonl with one JSON record per chunk:

    {
      "id": "<category>::<filename>::chunk_<idx>",
      "category": "<category>",
      "attack_type": "<attack_type or category>",
      "source_path": "RAG_docs/<category>/<filename>.txt",
      "chunk_index": <int>,
      "section_type": "explanation" | "example",
      "text": "...chunk text...",
      "embedding": [ ... float32 list ... ]
    }
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RAG_ROOT = Path("Research/RAG_docs")
OUTPUT_FILE = Path("knowledge_store.jsonl")
EMBED_MODEL = "text-embedding-3-large"

# Explanation chunks can be bigger; examples are kept whole.
EXPLANATION_MAX_CHARS = 1600
BATCH_SIZE = 16  # number of chunks per embeddings API call


# ---------------------------------------------------------------------------
# Env + client
# ---------------------------------------------------------------------------

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_all_txt_docs(root: Path) -> List[Dict[str, Any]]:
    """Recursively read all .txt files under RAG_docs/, tagging by category."""
    docs: List[Dict[str, Any]] = []
    for path in root.rglob("*.txt"):
        if not path.is_file():
            continue
        # category is the first folder under RAG_docs
        try:
            category = path.relative_to(root).parts[0]
        except IndexError:
            # If somehow the file is directly under RAG_docs without a subfolder
            category = "unknown"
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue
        docs.append(
            {
                "category": category,
                "path": path,
                "text": text,
            }
        )
    return docs


def parse_attack_type(text: str, fallback: str) -> str:
    """
    Try to extract AttackType from the header, e.g.:

        Title: Something (AttackType: access_control)

    or:

        Vulnerability Name: access_control

    If not found, use the folder category as a fallback.
    """
    m = re.search(r"AttackType:\s*([a-zA-Z0-9_]+)", text)
    if m:
        return m.group(1).strip()

    m2 = re.search(r"Vulnerability Name:\s*([a-zA-Z0-9_]+)", text)
    if m2:
        return m2.group(1).strip()

    return fallback


def split_explanation_and_samples(text: str):
    """
    Split doc into explanation vs samples sections.

    We look for a 'Samples' heading:

        Samples
        =======

    If not found, treat entire doc as explanation.
    """
    # Try to find 'Samples' as a heading
    match = re.search(r"^Samples\s*=*.*$", text, flags=re.MULTILINE)
    if not match:
        return text.strip(), ""

    idx = match.start()
    explanation = text[:idx].strip()
    samples = text[idx:].strip()
    return explanation, samples


def chunk_explanation(text: str, max_chars: int = EXPLANATION_MAX_CHARS) -> List[str]:
    """
    Chunk explanation text by paragraphs up to max_chars to keep them
    reasonably sized for embedding.
    """
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for p in paragraphs:
        addition_len = len(p) + (2 if current else 0)
        if current and len(current) + addition_len > max_chars:
            chunks.append(current)
            current = p
        else:
            current = p if not current else current + "\n\n" + p

    if current:
        chunks.append(current)

    return chunks


def split_samples_by_example(samples_text: str) -> List[str]:
    """
    Split the 'Samples' section into chunks by 'Example:' headings.
    Each returned string contains one example's title, notes, and code.

    If there are no 'Example:' headings, returns [samples_text].
    """
    if not samples_text:
        return []

    # Keep the 'Samples' heading attached to the first example
    # but we split on lines that start with 'Example:'
    # using a lookahead so we keep 'Example:' itself in the chunk.
    matches = list(re.finditer(r"^Example:\s.*$", samples_text, flags=re.MULTILINE))
    if not matches:
        return [samples_text.strip()]

    chunks: List[str] = []

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(samples_text)
        chunk = samples_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Call OpenAI embeddings API for a batch of texts."""
    if not texts:
        return []

    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [item.embedding for item in resp.data]


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    docs = read_all_txt_docs(RAG_ROOT)
    print(f"Found {len(docs)} RAG docs under {RAG_ROOT}")

    total_chunks = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as out_f:
        for doc in docs:
            category = doc["category"]
            path: Path = doc["path"]
            raw_text: str = doc["text"]

            attack_type = parse_attack_type(raw_text, fallback=category)

            explanation_text, samples_text = split_explanation_and_samples(raw_text)

            explanation_chunks = chunk_explanation(explanation_text)
            example_chunks = split_samples_by_example(samples_text)

            # Build a list of (section_type, chunk_text) for embedding
            all_sections: List[Dict[str, Any]] = []

            for chunk_text in explanation_chunks:
                all_sections.append(
                    {
                        "section_type": "explanation",
                        "text": chunk_text,
                    }
                )

            for chunk_text in example_chunks:
                all_sections.append(
                    {
                        "section_type": "example",
                        "text": chunk_text,
                    }
                )

            if not all_sections:
                continue

            # Embed in batches for efficiency
            batch_start = 0
            chunk_index = 0

            while batch_start < len(all_sections):
                batch = all_sections[batch_start : batch_start + BATCH_SIZE]
                batch_texts = [s["text"] for s in batch]
                embeddings = embed_batch(batch_texts)

                for local_idx, (section, emb) in enumerate(zip(batch, embeddings)):
                    record = {
                        "id": f"{category}::{path.name}::chunk_{chunk_index}",
                        "category": category,
                        "attack_type": attack_type,
                        "source_path": str(path),
                        "chunk_index": chunk_index,
                        "section_type": section["section_type"],  # "explanation" or "example"
                        "text": section["text"],
                        "embedding": emb,
                    }
                    out_f.write(json.dumps(record) + "\n")
                    chunk_index += 1
                    total_chunks += 1

                batch_start += BATCH_SIZE

            print(f"Processed {path} → {chunk_index} chunks")

    print(f"Done. Wrote {total_chunks} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()