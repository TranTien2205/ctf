# Question: Question: lateral movement in-account

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

AssumeRole chains (walk roleArn -> assumedRoleUser.arn -> next hop's userIdentity), cross-account AssumeRole joined on sharedEventID, role-session names that change operator.

## Answer shape

eventTime + eventName + the verbatim field the question asked for +
which artifact (trail/access log/flow) it was quoted from.

## Pivot

Question not in the cloud plane -> `cross-*` to the host or network
class.
