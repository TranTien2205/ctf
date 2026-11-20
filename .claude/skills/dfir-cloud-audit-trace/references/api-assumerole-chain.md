# API pattern: AssumeRole chains

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`.requestParameters.roleArn` + `.roleSessionName` in, `.responseElements.assumedRoleUser.arn` out - the in/out pair links each session to the next; walk the chain by matching the new assumed-role arn to the next hop's userIdentity.

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
