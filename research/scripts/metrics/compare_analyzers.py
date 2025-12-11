"""
compare_analyzers.py

This script performs a system-level comparison of all vulnerability analyzers.
Instead of computing global metrics, it performs a side-by-side qualitative
comparison for each contract and each detected attack.

Responsibilities:
    • Load outputs from:
            - Slither normalized
            - Almanax
            - LLM raw
            - LLM rag
            - Ground-truth audit JSON
    • Align results for each contract by:
            - attack type (one of the 10 categories)
            - severity
            - affected line numbers
            - short descriptions
    • Produce a human-readable comparison table showing:
            - agreements
            - disagreements
            - missing or extra vulnerabilities
            - severity mismatches
            - ontology mismatches (SWC conflicts)
    • Export comparison results to:
            comparisons/<contract_id>.json
            comparisons/<contract_id>.md

Does NOT:
    • Calculate precision/recall/F1 (handled by compute_metrics.py)
    • Run Slither, Almanax, or any LLM models
    • Perform embeddings or retrieval
    • Parse or normalize raw Slither JSON

Used when:
    • Debugging specific disagreement cases
    • Understanding where LLMs outperform or fail vs. Slither/Almanax
    • Fine-tuning ontology mapping, severity scaling, and prompt quality
    • Preparing qualitative discussion for the research paper
"""
