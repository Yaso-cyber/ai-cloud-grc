"""Tests for the scanner, policy engine, risk scorer, and API."""

import json
import os
import sys

import pytest

# Make backend modules importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["MOCK_MODE"] = "true"
os.environ["STUB_AI"] = "true"


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def test_scanner_returns_findings():
    from scanner.aws_scanner import run_scan
    findings = run_scan()
    assert isinstance(findings, list)
    assert len(findings) > 0


def test_finding_schema():
    from scanner.aws_scanner import run_scan
    findings = run_scan()
    required_keys = {"id", "resource_type", "resource_id", "control_id", "description", "severity"}
    for f in findings:
        assert required_keys.issubset(f.keys()), f"Missing keys in finding: {f}"


# ---------------------------------------------------------------------------
# Policy engine
# ---------------------------------------------------------------------------

def test_evaluate_enriches_findings():
    from scanner.aws_scanner import run_scan
    from policy_engine.evaluator import evaluate
    enriched = evaluate(run_scan())
    for f in enriched:
        assert "severity_weight" in f
        assert "framework_refs" in f


def test_framework_summary():
    from scanner.aws_scanner import run_scan
    from policy_engine.evaluator import evaluate, framework_summary
    summary = framework_summary(evaluate(run_scan()))
    assert isinstance(summary, dict)
    assert len(summary) > 0


# ---------------------------------------------------------------------------
# Risk scorer
# ---------------------------------------------------------------------------

def test_score_range():
    from scanner.aws_scanner import run_scan
    from policy_engine.evaluator import evaluate
    from risk_scorer.scorer import score
    result = score(evaluate(run_scan()))
    assert 0 <= result["score"] <= 100
    assert result["level"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_empty_findings_score():
    from risk_scorer.scorer import score
    result = score([])
    assert result["score"] == 0


# ---------------------------------------------------------------------------
# AI assistant (stub mode)
# ---------------------------------------------------------------------------

def test_explain_stub():
    from ai_assistant.assistant import explain
    finding = {"control_id": "S3-001", "resource_id": "test-bucket",
               "description": "Public bucket", "severity": "HIGH"}
    result = explain(finding)
    assert isinstance(result, str)
    assert len(result) > 0


def test_remediate_stub():
    from ai_assistant.assistant import remediate
    finding = {"control_id": "IAM-001", "resource_id": "user1",
               "description": "No MFA", "severity": "CRITICAL",
               "remediation_hint": "Enable MFA"}
    result = remediate(finding)
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def test_api_health():
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_api_scan():
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    resp = client.get("/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert "findings" in data
    assert "risk" in data
    assert "framework_summary" in data


def test_api_explain():
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    payload = {"finding": {"control_id": "S3-001", "resource_id": "bucket",
                           "description": "Public ACL", "severity": "HIGH"}}
    resp = client.post("/explain", json=payload)
    assert resp.status_code == 200
    assert "explanation" in resp.json()
