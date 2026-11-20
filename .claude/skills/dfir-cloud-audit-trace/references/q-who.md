# Question: Question: who did it

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

userIdentity.arn/session name/accessKeyId - the last `/` segment on assumed-role arns. Attribute by identity record, never by sourceIPAddress alone (NAT/shared egress).

## Answer shape

eventTime + eventName + the verbatim field the question asked for +
which artifact (trail/access log/flow) it was quoted from.

## Pivot

Question not in the cloud plane -> `cross-*` to the host or network
class.
