from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# ROOT = backend directory
LOCAL_ROOT = Path(__file__).resolve().parents[0]

# Load .env
load_dotenv(LOCAL_ROOT / ".env")

client = OpenAI()

PROMPT_PATH = LOCAL_ROOT / "prompts" / "generate_contracts.txt"
print(PROMPT_PATH)
if not PROMPT_PATH.exists():
    raise FileNotFoundError(f"Generation prompt not found: {PROMPT_PATH}")

PROMPT = PROMPT_PATH.read_text()


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
    "unprotected_self_destruct",
]


def extract_output_text(resp):
    """Handles OpenAI ChatCompletions API response."""
    try:
        # Standard ChatCompletions API response
        if hasattr(resp, 'choices') and resp.choices:
            return resp.choices[0].message.content

        # Legacy format (if any)
        if hasattr(resp, "output_text") and resp.output_text:
            return resp.output_text

        # Fallback for other formats
        if hasattr(resp, 'outputs'):
            return resp.outputs[0].content[0].text

    except Exception as e:
        raise RuntimeError(f"Unable to extract LLM output: {e}")

    raise RuntimeError("Unable to extract LLM output: Unknown response format")


def parse_llm_output(raw_output: str):
    """
    Extract JSON block + malicious contract only.
    """

    # -------- Extract JSON --------
    start = raw_output.find("{")
    if start == -1:
        raise RuntimeError("No JSON found.")

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
        raise RuntimeError("JSON block not closed.")

    json_block = raw_output[start:end].strip()

    # -------- Extract malicious contract --------
    remainder = raw_output[end:]
    if "// MALICIOUS CONTRACT" not in remainder:
        raise RuntimeError("Missing malicious contract marker.")

    malicious = remainder.split("// MALICIOUS CONTRACT", 1)[1].strip()

    return json_block, malicious


def generate_malicious_contract(attack_type: str, model: str):
    if attack_type not in ATTACK_TYPES:
        raise ValueError(f"Invalid attack type: {attack_type}")

    prompt = PROMPT.format(
        attack_type=attack_type,
        contract_id="web_generated"
    )

    if model == "gpt-5.1":
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
    else:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )

    raw_output = extract_output_text(resp)
    metadata, malicious = parse_llm_output(raw_output)

    return metadata, malicious
