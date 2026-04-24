# S3 Security Policies — OPA/Rego

package grc.s3

import future.keywords.if
import future.keywords.contains

# Deny public ACL
deny contains msg if {
    input.acl == "public-read"
    msg := sprintf("S3-001: Bucket '%v' has public-read ACL. Set to private.", [input.bucket_name])
}

deny contains msg if {
    input.acl == "public-read-write"
    msg := sprintf("S3-001: Bucket '%v' has public-read-write ACL. Set to private.", [input.bucket_name])
}

# Deny missing versioning
deny contains msg if {
    input.versioning != "Enabled"
    msg := sprintf("S3-002: Bucket '%v' does not have versioning enabled.", [input.bucket_name])
}

# Deny missing server-side encryption
deny contains msg if {
    not input.server_side_encryption
    msg := sprintf("S3-003: Bucket '%v' does not have server-side encryption enabled.", [input.bucket_name])
}
