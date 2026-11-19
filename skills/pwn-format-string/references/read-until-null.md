# Read until null — the %s truncation


%s reads a C string — stops at the first \x00. A flag or pointer whose
bytes contain an early \x00 truncates the read.

## Steps

1. %s prints until \x00 — a pointer's bytes containing 0x00 truncate.
2. For flag strings this rarely matters.
3. For binary data (a struct, a pointer) expect early truncation.

## Falsifier

None; a truncation artifact to expect. To read past \x00, bump the
pointer and %s again.
