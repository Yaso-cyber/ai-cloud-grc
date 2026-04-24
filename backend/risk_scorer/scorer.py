"""
Risk Scorer — computes an overall risk score (0–100) from evaluated findings.
Higher score = more risk.
"""

from typing import Any


def score(evaluated_findings: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Returns:
        {
          "score": float,           # 0–100, higher is worse
          "level": str,             # CRITICAL | HIGH | MEDIUM | LOW
          "breakdown": {severity: count},
          "top_findings": list      # top 3 by weight
        }
    """
    if not evaluated_findings:
        return {"score": 0, "level": "LOW", "breakdown": {}, "top_findings": []}

    breakdown: dict[str, int] = {}
    total_weight = 0

    for f in evaluated_findings:
        sev = f.get("severity", "LOW")
        breakdown[sev] = breakdown.get(sev, 0) + 1
        total_weight += f.get("severity_weight", 2)

    # Normalize to 0–100 (cap at 100). Each finding can contribute up to 10 pts.
    max_possible = len(evaluated_findings) * 10
    normalized = min(round((total_weight / max_possible) * 100, 1), 100.0)

    if normalized >= 80:
        level = "CRITICAL"
    elif normalized >= 60:
        level = "HIGH"
    elif normalized >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    top_findings = sorted(
        evaluated_findings,
        key=lambda x: x.get("severity_weight", 0),
        reverse=True,
    )[:3]

    return {
        "score": normalized,
        "level": level,
        "breakdown": breakdown,
        "top_findings": top_findings,
    }
