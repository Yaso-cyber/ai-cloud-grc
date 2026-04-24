"""
AI Assistant — uses OpenAI (or a stub) to explain findings in plain English
and generate remediation playbooks.
"""

import os
from typing import Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("AI_MODEL", "gpt-4o")
STUB_MODE = not OPENAI_API_KEY or os.getenv("STUB_AI", "false").lower() == "true"


def _call_openai(system: str, user: str) -> str:
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=600,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def _stub_explain(finding: dict[str, Any]) -> str:
    return (
        f"[STUB] Finding '{finding.get('control_id')}' on resource "
        f"'{finding.get('resource_id')}': {finding.get('description')} "
        f"Severity: {finding.get('severity')}. Set OPENAI_API_KEY to get real explanations."
    )


def _stub_remediate(finding: dict[str, Any]) -> str:
    hint = finding.get("remediation_hint", "No hint available.")
    return (
        f"[STUB] Remediation for '{finding.get('control_id')}': {hint} "
        "Set OPENAI_API_KEY to get a full step-by-step playbook."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explain(finding: dict[str, Any]) -> str:
    """Return a plain-English explanation of a finding."""
    if STUB_MODE:
        return _stub_explain(finding)

    system = (
        "You are a cloud security expert. Explain cloud security findings "
        "to a non-technical audience in 2-3 sentences. Be clear and concise."
    )
    user = (
        f"Resource type: {finding.get('resource_type')}\n"
        f"Resource ID: {finding.get('resource_id')}\n"
        f"Control: {finding.get('control_id')} — {finding.get('control_title', '')}\n"
        f"Description: {finding.get('description')}\n"
        f"Severity: {finding.get('severity')}\n"
        "Explain this finding in plain English."
    )
    return _call_openai(system, user)


def remediate(finding: dict[str, Any]) -> str:
    """Return a step-by-step remediation playbook for a finding."""
    if STUB_MODE:
        return _stub_remediate(finding)

    system = (
        "You are a cloud security engineer. Provide a concise, step-by-step "
        "remediation playbook for the given cloud security finding. Include "
        "CLI commands where applicable. Format as a numbered list."
    )
    user = (
        f"Resource type: {finding.get('resource_type')}\n"
        f"Resource ID: {finding.get('resource_id')}\n"
        f"Control: {finding.get('control_id')} — {finding.get('control_title', '')}\n"
        f"Description: {finding.get('description')}\n"
        f"Hint: {finding.get('remediation_hint', '')}\n"
        f"Framework refs: {finding.get('framework_refs', {})}\n"
        "Provide a remediation playbook."
    )
    return _call_openai(system, user)


def summarize_risk(risk_result: dict[str, Any], framework_summary: dict[str, list[str]]) -> str:
    """Return an executive summary of the overall risk posture."""
    if STUB_MODE:
        return (
            f"[STUB] Risk score: {risk_result.get('score')}/100 ({risk_result.get('level')}). "
            f"Breakdown: {risk_result.get('breakdown')}. "
            "Set OPENAI_API_KEY for a full narrative summary."
        )

    system = (
        "You are a CISO writing an executive risk summary. Be concise (3-4 sentences), "
        "highlight top risks, and recommend immediate actions."
    )
    user = (
        f"Risk score: {risk_result.get('score')}/100 ({risk_result.get('level')})\n"
        f"Finding breakdown by severity: {risk_result.get('breakdown')}\n"
        f"Failing compliance controls: {framework_summary}\n"
        "Write an executive risk summary."
    )
    return _call_openai(system, user)
