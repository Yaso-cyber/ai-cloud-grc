"""
FastAPI application — main entry point for the ai-cloud-grc backend.
"""

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scanner.aws_scanner import run_scan
from policy_engine.evaluator import evaluate, framework_summary
from risk_scorer.scorer import score
from ai_assistant.assistant import explain, remediate, summarize_risk

app = FastAPI(
    title="ai-cloud-grc API",
    description="AI-driven Cloud GRC Toolkit backend",
    version="0.1.0",
)

# Allow the React dev server and deployed frontend
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class FindingIn(BaseModel):
    finding: dict[str, Any]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/scan")
def scan():
    """Run the scanner, evaluate findings, and return risk score."""
    raw = run_scan()
    enriched = evaluate(raw)
    risk = score(enriched)
    fw_summary = framework_summary(enriched)
    return {
        "findings": enriched,
        "risk": risk,
        "framework_summary": fw_summary,
    }


@app.post("/explain")
def explain_finding(body: FindingIn):
    """Return a plain-English explanation of a finding."""
    try:
        result = explain(body.finding)
        return {"explanation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/remediate")
def remediate_finding(body: FindingIn):
    """Return a remediation playbook for a finding."""
    try:
        result = remediate(body.finding)
        return {"playbook": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summary")
def risk_summary():
    """Return an AI-generated executive risk summary."""
    raw = run_scan()
    enriched = evaluate(raw)
    risk = score(enriched)
    fw_summary = framework_summary(enriched)
    try:
        narrative = summarize_risk(risk, fw_summary)
    except Exception as e:
        narrative = f"Error generating summary: {e}"
    return {
        "risk": risk,
        "framework_summary": fw_summary,
        "narrative": narrative,
    }
