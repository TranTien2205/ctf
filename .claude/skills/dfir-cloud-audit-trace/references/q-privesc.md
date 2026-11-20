# Question: Question: privilege escalation

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

AttachUserPolicy/AttachRolePolicy (managed grant), PutUserPolicy/PutRolePolicy (inline), UpdateAssumeRolePolicy (trust rewrite = who may now assume), Add*Permission (lambda), CreatePolicyVersion (edit a managed policy in-place).

## Answer shape

eventTime + eventName + the verbatim field the question asked for +
which artifact (trail/access log/flow) it was quoted from.

## Pivot

Question not in the cloud plane -> `cross-*` to the host or network
class.
