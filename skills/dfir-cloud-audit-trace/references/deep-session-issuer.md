# Deep dive: Deep: sessionContext.sessionIssuer

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

On AssumedRole records, `.sessionContext.sessionIssuer` carries the ISSUING identity (type, userName, arn) - the identity that minted the session, which is the attribution one level up.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
