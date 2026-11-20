# The falsifier — all operational

Every record type returns only operational data and the cert names
no host the challenge didn't already supply → the answer isn't in
the live records; only an archived/transparency source could carry
it. Pivot to crt.sh/archive/passive or reclassify.

## What operational means

- A/AAAA/MX/NS point at real infrastructure, no flag strings.
- TXT holds only SPF/verification tokens, nothing planted.
- SANs name only hosts already supplied.
Then the answer is historical — crt.sh/archive/passive — or in a
different class entirely.

## After the falsifier

Do not re-query the same records — the live space is clean; the answer moved to a historical source or a different class.

## When clean

All-operational → note it, then check crt.sh/archive/passive for what the records held before; or reclassify.

## The boundary

An all-operational set means the live records are clean — the answer, if any, is historical or web-side.
