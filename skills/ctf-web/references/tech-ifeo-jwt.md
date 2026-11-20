# Technique: JWT family

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

alg none, HS256<->RS256 confusion, weak HMAC secret brute, kid injection (traversal/SQLi), jku/x5u hosting - session_dissect.py names which applies.

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
