# The artifact x question matrix

Routing module for `dfir-sherlock-triage`. Question text +
artifact inventory -> one depth file. The router never answers
the question; it names who does.

aq-* cells carry the authoritative pairing: every
artifact against every question type, graded
strong-owner/partial/ruled-out with the depth file.

## Pivot

Question literal -> its q-* module; artifact absent -> fal-*.
