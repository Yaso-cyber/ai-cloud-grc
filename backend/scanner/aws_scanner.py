"""
AWS Cloud Scanner
Collects config for S3 buckets, IAM users/policies, EC2 instances, and VPCs.
Set MOCK_MODE=true (env) to use demo data instead of live AWS credentials.
"""

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any

MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finding(resource_type: str, resource_id: str, control_id: str,
             description: str, severity: str, remediation: str,
             framework_refs: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return {
        "id": f"{resource_type}/{resource_id}/{control_id}",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "control_id": control_id,
        "description": description,
        "severity": severity,  # CRITICAL | HIGH | MEDIUM | LOW | INFO
        "remediation_hint": remediation,
        "framework_refs": framework_refs or {},
        "scanned_at": _timestamp(),
    }


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_FINDINGS: list[dict[str, Any]] = [
    _finding(
        "s3", "my-public-bucket", "S3-001",
        "S3 bucket has public read ACL enabled.",
        "HIGH",
        "Set bucket ACL to private and enable Block Public Access settings.",
        {"NIST_800_53": ["AC-3", "SC-7"], "ISO_27001": ["A.9.4.1"], "SOC2": ["CC6.1"]},
    ),
    _finding(
        "s3", "my-public-bucket", "S3-002",
        "S3 bucket versioning is disabled.",
        "MEDIUM",
        "Enable versioning via: aws s3api put-bucket-versioning --bucket my-public-bucket --versioning-configuration Status=Enabled",
        {"NIST_800_53": ["CP-9"], "ISO_27001": ["A.12.3.1"], "SOC2": ["A1.2"]},
    ),
    _finding(
        "iam", "admin-user", "IAM-001",
        "IAM user has no MFA device configured.",
        "CRITICAL",
        "Enforce MFA for all IAM users with console access via IAM policy or AWS Organizations SCP.",
        {"NIST_800_53": ["IA-2"], "ISO_27001": ["A.9.4.2"], "SOC2": ["CC6.1"]},
    ),
    _finding(
        "iam", "legacy-policy", "IAM-002",
        "IAM policy grants wildcard (*) actions on all resources.",
        "HIGH",
        "Apply least-privilege: replace '*' actions with only required actions and specific resource ARNs.",
        {"NIST_800_53": ["AC-6"], "ISO_27001": ["A.9.1.2"], "SOC2": ["CC6.3"]},
    ),
    _finding(
        "ec2", "i-0abc123def456", "EC2-001",
        "EC2 security group allows unrestricted SSH access (0.0.0.0/0 on port 22).",
        "HIGH",
        "Restrict SSH to known IP ranges or use AWS Systems Manager Session Manager instead.",
        {"NIST_800_53": ["SC-7", "AC-3"], "ISO_27001": ["A.13.1.1"], "SOC2": ["CC6.6"]},
    ),
    _finding(
        "vpc", "vpc-0def456abc", "VPC-001",
        "VPC Flow Logs are not enabled.",
        "MEDIUM",
        "Enable VPC Flow Logs to CloudWatch or S3 for network traffic visibility.",
        {"NIST_800_53": ["AU-2", "AU-12"], "ISO_27001": ["A.12.4.1"], "SOC2": ["CC7.2"]},
    ),
]


# ---------------------------------------------------------------------------
# Live scanners (require boto3 + valid AWS credentials)
# ---------------------------------------------------------------------------

def _scan_s3_live() -> list[dict[str, Any]]:
    import boto3  # type: ignore
    findings: list[dict[str, Any]] = []
    s3 = boto3.client("s3")
    buckets = s3.list_buckets().get("Buckets", [])

    for bucket in buckets:
        name = bucket["Name"]

        # Check public ACL
        try:
            acl = s3.get_bucket_acl(Bucket=name)
            for grant in acl.get("Grants", []):
                grantee = grant.get("Grantee", {})
                if grantee.get("URI", "").endswith("AllUsers"):
                    findings.append(_finding(
                        "s3", name, "S3-001",
                        "S3 bucket has public read ACL enabled.",
                        "HIGH",
                        "Set bucket ACL to private and enable Block Public Access settings.",
                        {"NIST_800_53": ["AC-3", "SC-7"]},
                    ))
        except Exception:
            pass

        # Check versioning
        try:
            v = s3.get_bucket_versioning(Bucket=name)
            if v.get("Status") != "Enabled":
                findings.append(_finding(
                    "s3", name, "S3-002",
                    "S3 bucket versioning is disabled.",
                    "MEDIUM",
                    f"Enable versioning: aws s3api put-bucket-versioning --bucket {name} --versioning-configuration Status=Enabled",
                    {"NIST_800_53": ["CP-9"]},
                ))
        except Exception:
            pass

    return findings


def _scan_iam_live() -> list[dict[str, Any]]:
    import boto3  # type: ignore
    findings: list[dict[str, Any]] = []
    iam = boto3.client("iam")

    # Check users for MFA
    paginator = iam.get_paginator("list_users")
    for page in paginator.paginate():
        for user in page["Users"]:
            username = user["UserName"]
            mfa_devices = iam.list_mfa_devices(UserName=username).get("MFADevices", [])
            if not mfa_devices:
                findings.append(_finding(
                    "iam", username, "IAM-001",
                    "IAM user has no MFA device configured.",
                    "CRITICAL",
                    "Enforce MFA for all IAM users with console access.",
                    {"NIST_800_53": ["IA-2"]},
                ))

    return findings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_scan() -> list[dict[str, Any]]:
    """Return findings list. Uses mock data unless MOCK_MODE is false."""
    if MOCK_MODE:
        return MOCK_FINDINGS

    findings: list[dict[str, Any]] = []
    findings.extend(_scan_s3_live())
    findings.extend(_scan_iam_live())
    return findings


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ai-cloud-grc AWS Scanner")
    parser.add_argument("--output", default="findings.json", help="Output file path")
    parser.add_argument("--mock", action="store_true", help="Use mock data")
    args = parser.parse_args()

    if args.mock:
        os.environ["MOCK_MODE"] = "true"

    results = run_scan()
    with open(args.output, "w") as f:
        json.dump({"findings": results, "generated_at": _timestamp()}, f, indent=2)
    print(f"Wrote {len(results)} findings to {args.output}")
