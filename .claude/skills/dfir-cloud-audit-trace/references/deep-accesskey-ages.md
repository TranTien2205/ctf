# Deep dive: Deep: accessKeyId forensics

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

The AKIA*/ASIA* prefix distinguishes long-term keys (IAM user) from temp session keys (STS) - an ASIA* accessKeyId means the calls came through a session, and the sessionIssuer question applies.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
