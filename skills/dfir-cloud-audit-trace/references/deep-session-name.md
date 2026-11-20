# Deep dive: Deep: role session names

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`.userIdentity.arn | split("/") | last` - operator-chosen per AssumeRole call (roleSessionName); 'cli-session', an email, or a tool name are all real shapes; measured here it printed `cli-session`.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
