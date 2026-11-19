# Remote vs local — the libc must match


Local success means nothing if the remote libc differs — re-derive
every offset against the REMOTE libc (shipped file or identified
version).

## The rule

- The challenge ships a libc → use THAT file for every offset.
- No shipped libc → leak and identify (a few known symbol distances
  fingerprint the version).
- Docker base image stated → pull its libc version.

## Falsifier

You can't determine the remote libc: the exploit carries an
unverifiable assumption — find a leak-based identifier first.
