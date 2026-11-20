# API pattern: Recon-then-act boundary

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`List*`/`Get*`/`Describe*` burst then the first `Create*`/`Put*`/`Delete*` - the first write's eventTime is the usual Sherlock answer ('when did the attacker first modify'). Filter readOnly!=true or match on the write-name families.

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
