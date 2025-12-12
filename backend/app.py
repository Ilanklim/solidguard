from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Import classifier
from backend.contract_classifier import (
    classify_raw_contract_text,
    classify_rag_contract_text,
)

# Import generator
from backend.contract_generator import generate_malicious_contract

ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(ROOT)

if PARENT not in sys.path:
    sys.path.append(PARENT)

ALLOWED_MODELS = ["gpt-4.1", "gpt-4.1-mini", "gpt-5.1"]

# Model name mapping for actual OpenAI API calls
MODEL_MAPPING = {
    "gpt-4.1-mini": "gpt-4.1-mini",
    "gpt-4.1": "gpt-4.1",
    "gpt-5.1": "gpt-5.1",
}

app = FastAPI(
    title="SolidGuard Backend API",
    description="Smart contract vulnerability classifier + generator with selectable models",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------- Pydantic Models -----------------------
class ClassificationRequest(BaseModel):
    contract_text: str
    mode: str = "raw"        # raw or rag
    model: str = "gpt-5.1"   # any allowed model


class GenerationRequest(BaseModel):
    attack_type: str
    model: str = "gpt-5.1"   # any allowed model


# ---------------------- Routes -----------------------
@app.get("/")
def home():
    return {"message": "SolidGuard backend is running!"}


# ---------- CLASSIFICATION ----------
@app.post("/classify")
def classify(req: ClassificationRequest):

    if req.model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Allowed: {ALLOWED_MODELS}")

    if not req.contract_text.strip():
        raise HTTPException(status_code=400, detail="Contract text is empty.")

    try:
        # Use the mapped model name for API calls
        actual_model = MODEL_MAPPING.get(req.model, req.model)

        if req.mode == "raw":
            result = classify_raw_contract_text(contract_text=req.contract_text, model=actual_model)

        elif req.mode == "rag":
            result = classify_rag_contract_text(contract_text=req.contract_text, model=actual_model)

        else:
            raise HTTPException(status_code=400, detail="Mode must be 'raw' or 'rag'")

        return {"success": True, "mode": req.mode, "model": req.model, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- GENERATION ----------
@app.post("/generate")
def generate(req: GenerationRequest):

    if req.model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Allowed: {ALLOWED_MODELS}")

    try:
        # Use the mapped model name for API calls
        actual_model = MODEL_MAPPING.get(req.model, req.model)

        metadata, malicious = generate_malicious_contract(
            req.attack_type,
            actual_model
        )

        return {
            "success": True,
            "attack_type": req.attack_type,
            "model": req.model,
            "metadata": metadata,
            "malicious": malicious,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ---------- Local Debug ----------
if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
