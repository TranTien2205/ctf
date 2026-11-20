# Deep dive: Deep: ConsoleLogin vs CheckMfa

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

CheckMfa is the MFA-capability listing (MfaType in additionalEventData) - it can appear WITHOUT a login success; ConsoleLogin.MFAUsed is the per-login answer.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
