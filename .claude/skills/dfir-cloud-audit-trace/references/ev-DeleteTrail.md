# Event: DeleteTrail (cloudtrail)

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Answers "trail destroyed". Read: `.requestParameters.name - lands in the trail until success`.

## Record shape

eventSource `cloudtrail.amazonaws.com` (or the *-data caveat on data
events); the fields above are the columns to quote for the question
this call answers. `errorCode` present means the call was DENIED -
still evidence of attempt.

## Evidence rule

eventName + the verbatim requestParameters/responseElements field;
'they called X' without the quoted target field is surface.

## Pivot

Event mapped -> the question module `q-*` that consumes it, or
`api-*` for the pattern it belongs to.
