# The last mile — writing the chain card

After the flag verifies, write the chain card so the next fmtstr match
recalls the path.

## The card

- signals: the observables (printf-of-input, %p reflection, the offset).
- first_confirming_probe: the %p send + the marker scan.
- the chain: leak -> offset -> plant -> write -> read-back -> fire.
- traps: the RELRO check, the alignment, the count arithmetic, the glibc
  version for hooks, the arg-window limits.
- blast_radius: the %n write corrupts a live pointer — a misfire crashes
  the service.

## Record

    python3 tools/classify_solve.py --chain <id>

A fmtstr solved and carded makes the next one a chain_match hit rather
than a fresh derivation.
