# API pattern: CreateLoginProfile / UpdateLoginProfile

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Adds or changes a CONSOLE password on a key-only identity - `requestParameters.userName`; pairs with a later ConsoleLogin Success on the same userName.

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
