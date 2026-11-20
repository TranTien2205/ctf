# API pattern: Destruction + cover

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`DeleteObjects`/`DeleteBucket` (S3 data is data events off by default - only the bucket-level calls show), `DeleteTrail`/`StopLogging`/`UpdateTrail` on cloudtrail itself, `DeleteLogGroup`/`DeleteLogStream` on cloudwatchlogs - the anti-forensics shape in the same trail.

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
