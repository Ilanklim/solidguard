"""
audit_pdf_to_json.py

This script converts full smart contract audit reports (PDFs) into
normalized vulnerability JSON files compatible with the project's
10-category ontology and downstream metric/comparison pipelines.

Responsibilities:
    • Load a PDF audit file and extract raw text (via pypdf or similar)
    • Determine whether the audit references ANY of the 10 supported attack types
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
    • If the audit contains ZERO relevant findings:
         → Write output: "Does not reference 10 attack types"
    • If the audit DOES contain relevant findings:
         → Send the extracted text to the audit_pdf_to_json LLM prompt
         → Parse only findings belonging to the 10 categories
         → Normalize severity, description, line numbers, and SWC references
         → Produce a final JSON object matching this schema:

            {
              "id": "{{contract_id}}",
              "solidity": "^0.8.20",
              "attacks": [...]
            }

    • Write the resulting structured JSON into:
            data/audits/normalized/<contract_id>.json

Does NOT:
    • Perform vulnerability classification on contracts
    • Generate synthetic contracts
    • Run Slither or Almanax
    • Compare analyzer results or compute metrics

Used when:
    • Building ground-truth datasets from real audit PDFs
    • Validating LLM/Slither/Almanax agreement
    • Creating normalized input for compute_metrics.py and compare_analyzers.py
"""

