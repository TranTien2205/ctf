# Technique: XXE out-of-band

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Blind XXE -> external DTD on your host -> the DTD itself carries the file-read payload and exfils via error/URL - two-stage when inline entities are blocked.

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
