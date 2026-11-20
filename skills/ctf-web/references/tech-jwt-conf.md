# Technique: JWT confusion deep

Depth module for `ctf-web`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

RS256->HS256 with the public key as HMAC secret - works when the lib doesn't pin alg; the public key must be reachable (JWKS endpoint or the cert itself).

## Evidence rule

The technique claim still needs the verbatim response or artifact -
a technique name is routing information, not a finding.

## Pivot

Technique identified -> the shared file or class skill carrying its
payloads.
