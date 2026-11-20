# Matrix: M365 UAL - from where

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

For M365 UAL, "from where" resolves through sourceIPAddress/ipAddress + userAgent - not geography.
The record is the Operation row; the base module is `m365-ual.md` - read it for the
field names and the traps before quoting.

## Falsifier

If the record named above is absent AND the artifact is confirmed
parsed, the artifact did not produce this answer - record the negative
and move to the next cell or family.
