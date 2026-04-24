"""
Policy Engine — evaluates findings against control rules and maps them to
compliance frameworks (NIST 800-53, ISO 27001, SOC 2).
"""

from typing import Any

# ---------------------------------------------------------------------------
# Control definitions: control_id → metadata
# ---------------------------------------------------------------------------

CONTROLS: dict[str, dict[str, Any]] = {
    "S3-001": {
        "title": "S3 Public Access",
        "severity_weight": 8,
        "frameworks": {"NIST_800_53": ["AC-3", "SC-7"], "ISO_27001": ["A.9.4.1"], "SOC2": ["CC6.1"]},
    },
    "S3-002": {
        "title": "S3 Versioning Disabled",
        "severity_weight": 4,
        "frameworks": {"NIST_800_53": ["CP-9"], "ISO_27001": ["A.12.3.1"], "SOC2": ["A1.2"]},
    },
    "IAM-001": {
        "title": "IAM User Missing MFA",
        "severity_weight": 10,
        "frameworks": {"NIST_800_53": ["IA-2"], "ISO_27001": ["A.9.4.2"], "SOC2": ["CC6.1"]},
    },
    "IAM-002": {
        "title": "Wildcard IAM Policy",
        "severity_weight": 8,
        "frameworks": {"NIST_800_53": ["AC-6"], "ISO_27001": ["A.9.1.2"], "SOC2": ["CC6.3"]},
    },
    "EC2-001": {
        "title": "Unrestricted SSH Access",
        "severity_weight": 8,
        "frameworks": {"NIST_800_53": ["SC-7", "AC-3"], "ISO_27001": ["A.13.1.1"], "SOC2": ["CC6.6"]},
    },
    "VPC-001": {
        "title": "VPC Flow Logs Disabled",
        "severity_weight": 4,
        "frameworks": {"NIST_800_53": ["AU-2", "AU-12"], "ISO_27001": ["A.12.4.1"], "SOC2": ["CC7.2"]},
    },
}

SEVERITY_WEIGHTS = {
    "CRITICAL": 10,
    "HIGH": 8,
    "MEDIUM": 4,
    "LOW": 2,
    "INFO": 0,
}


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def evaluate(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Enrich each finding with control metadata and framework mappings."""
    enriched = []
    for f in findings:
        ctrl = CONTROLS.get(f["control_id"], {})
        enriched.append({
            **f,
            "control_title": ctrl.get("title", f["control_id"]),
            "severity_weight": ctrl.get("severity_weight", SEVERITY_WEIGHTS.get(f.get("severity", "LOW"), 2)),
            "framework_refs": f.get("framework_refs") or ctrl.get("frameworks", {}),
        })
    return enriched


def framework_summary(evaluated_findings: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Return a map of framework → list of failing control IDs."""
    summary: dict[str, list[str]] = {}
    for f in evaluated_findings:
        for framework, controls in f.get("framework_refs", {}).items():
            summary.setdefault(framework, [])
            for ctrl in controls:
                if ctrl not in summary[framework]:
                    summary[framework].append(ctrl)
    return summary
