# API pattern: GetCallerIdentity - first touch

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`sts.amazonaws.com` `GetCallerIdentity` is the canonical first touch with stolen credentials - it answers 'whose key is this' and costs the caller nothing. Its `.userIdentity.accessKeyId` is the pivot for the rest of the trail.

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
