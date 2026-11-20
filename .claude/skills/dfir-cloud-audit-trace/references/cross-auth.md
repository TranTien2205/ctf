# Cross: authentication-trace

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

A host logon is not a control-plane call - 4624/4625 and wtmp semantics live in `../dfir-authentication-trace/`; the ConsoleLogin/Entra/Okta records here are the CLOUD side of the same 'who got in' question.

## Pivot

Boundary applies -> route, do not stretch the claim.
