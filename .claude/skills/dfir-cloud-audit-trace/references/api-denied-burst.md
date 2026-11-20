# API pattern: AccessDenied burst = probing

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

A run of errorCode=AccessDenied records on escalating sensitive calls (ListBuckets, GetObject, CreateAccessKey attempts) is the permission-probing shape - count per accessKeyId + errorCode (the SKILL.md group_by jq).

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
