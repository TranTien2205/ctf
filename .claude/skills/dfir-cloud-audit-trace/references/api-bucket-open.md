# API pattern: Bucket policy/acl opens

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`PutBucketPolicy`, `PutBucketAcl`, `DeleteBucketPolicy`, `PutBucketVersioning`, `PutPublicAccessBlock` (both directions!) - `.requestParameters.bucketName` names which bucket was opened or closed.

## Evidence rule

Name the eventName and quote requestParameters/responseElements
verbatim - a pattern label without the record is a candidate.

## Pivot

Pattern identified -> `q-*` for the answer shape, or `s3-*`/`gd-*`/
`vpc-*` when the question leaves CloudTrail.
