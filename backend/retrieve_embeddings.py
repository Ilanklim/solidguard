"""
retrieve_embeddings.py

Lightweight semantic search engine for the RAG knowledge store.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# ------------------------------------------
# CONFIG
# ------------------------------------------
ROOT = Path(__file__).resolve().parents[1]   # backend/
STORE_PATH = ROOT / "knowledge_store.jsonl"
EMBED_MODEL = "text-embedding-3-large"

load_dotenv(ROOT / ".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in backend/.env")

client = OpenAI(api_key=api_key)


# ------------------------------------------
# KNOWLEDGE STORE CLASS
# ------------------------------------------
class KnowledgeStore:
    """
    Loads embeddings from knowledge_store.jsonl and enables vector search.
    """

    def __init__(self, path: Path = STORE_PATH):
        self.path = Path(path)
        self.records: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None

    def load(self):
        """Load all JSONL chunks + embeddings into memory."""
        if not self.path.exists():
            raise FileNotFoundError(f"Knowledge store missing: {self.path}")

        self.records = []
        vectors = []

        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                self.records.append(rec)
                vectors.append(rec["embedding"])

        self.embeddings = np.array(vectors, dtype="float32")
        print(f"[KnowledgeStore] Loaded {len(self.records)} chunks.")

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a query using OpenAI embeddings."""
        resp = client.embeddings.create(model=EMBED_MODEL, input=[text])
        return np.array(resp.data[0].embedding, dtype="float32")

    def retrieve(self, query: str, k: int = 5):
        """
        Return top-k most similar chunks for the query.
        """
        if self.embeddings is None:
            raise RuntimeError("Call .load() first.")

        q = self.embed_query(query)

        # Normalize
        norm_store = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norm_query = q / np.linalg.norm(q)

        # Cosine similarity
        sims = norm_store @ norm_query
        ranked = np.argsort(-sims)

        results = []
        for idx in ranked[:k]:
            rec = self.records[idx]
            results.append(
                {
                    "score": float(sims[idx]),
                    "category": rec.get("category", "unknown"),
                    "attack_type": rec.get("attack_type"),
                    "source": rec.get("source_path", rec.get("source")),
                    "chunk_index": rec.get("chunk_index", 0),
                    "text": rec.get("text", ""),
                }
            )

        return results
