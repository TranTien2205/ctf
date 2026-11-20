# API pattern: Attach/Put/Update policy

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`AttachUserPolicy`/`PutUserPolicy`/`AttachRolePolicy`/`UpdateAssumeRolePolicy` - `.requestParameters.policyArn` names the managed policy, `.policyDocument` the inline doc, `UpdateAssumeRolePolicy` edits who may assume a role (the trust-policy backdoor).

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
