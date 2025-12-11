"""
compute_metrics.py

This script computes quantitative evaluation metrics across all analyzers:
    • Slither (normalized)
    • Almanax (API or parsed)
    • Our LLM (raw)
    • Our LLM (rag)
    • Ground-truth audit JSON (from audit_pdf_to_json.py)

Responsibilities:
    • Load standardized vulnerability JSON files:
            slither_normalized.json
            almanax.json
            proj2_llm_raw.json
            proj2_llm_rag.json
            audit_ground_truth.json
    • Normalize fields (attack type, severity, line numbers, SWC refs)
    • Align findings across tools by:
            - attack category
            - description similarity
            - overlapping line ranges
    • Compute model quality metrics:
            - accuracy
            - precision / recall
            - F1 score
            - Jaccard index
            - false positive / false negative rates
    • Produce a consolidated metrics table and optional plots
    • Save results to:
            metrics/summary.json
            metrics/table.csv

Does NOT:
    • Run Slither
    • Call Almanax APIs
    • Perform LLM inference
    • Generate synthetic data
    • Create visual dashboards (optional external step)

Used when:
    • Evaluating how well each analyzer matches ground truth
    • Measuring improvements from RAG vs. raw
    • Comparing Slither/Almanax vs. LLM performance
    • Preparing final research paper results
"""
