# Scenario: Scenario: role-chain attribution

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Walk AssumeRole rows: requestParameters.roleArn + roleSessionName -> responseElements.assumedRoleUser.arn -> next hop's userIdentity. sourceIdentity at each hop names the human when set.

## Exit

Ends with a quoted record + window bounds, or a recorded negative and
the next family named.

## Pivot

Done -> `work-*` for reporting discipline.
