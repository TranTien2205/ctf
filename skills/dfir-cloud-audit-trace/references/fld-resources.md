# Field table: resources[]

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

ARN + accountId + type (AWS::IAM::Role, AWS::S3::Object...) - the object-level identity of what was touched.

## Pivot

Field mapped -> the ev-* module for the call that carries it.
