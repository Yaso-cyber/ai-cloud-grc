# IAM Security Policies — OPA/Rego

package grc.iam

import future.keywords.if
import future.keywords.contains

# Deny users without MFA
deny contains msg if {
    input.resource_type == "iam_user"
    count(input.mfa_devices) == 0
    msg := sprintf("IAM-001: IAM user '%v' has no MFA device configured.", [input.user_name])
}

# Deny wildcard actions in inline/managed policies
deny contains msg if {
    some statement in input.policy_statements
    statement.Effect == "Allow"
    statement.Action == "*"
    msg := sprintf("IAM-002: Policy '%v' grants wildcard (*) actions. Apply least-privilege.", [input.policy_name])
}

# Deny wildcard resources
deny contains msg if {
    some statement in input.policy_statements
    statement.Effect == "Allow"
    statement.Resource == "*"
    not statement.Condition  # only flag if no condition restricts it
    msg := sprintf("IAM-003: Policy '%v' grants access to all resources (*). Restrict to specific ARNs.", [input.policy_name])
}
