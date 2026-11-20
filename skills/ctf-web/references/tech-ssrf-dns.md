# Technique: SSRF DNS rebinding

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

TOCTOU on the resolve: the allowlist resolves once, the fetch resolves again to your record - needs a rebinding service or two A records.

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
