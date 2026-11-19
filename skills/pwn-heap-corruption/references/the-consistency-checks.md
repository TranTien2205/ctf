# Integrity checks by version — the gauntlet


A table of what glibc checks, when each was added — the gauntlet any
corruption must run.

- size alignment & minimum — always.
- next-size sanity on free — always.
- fastbin top double-free — early.
- tcache count bounds — 2.26+.
- tcache key — 2.29+.
- smallbin unlink fd<->bk consistency — 2.30+.
- corrupted top size — 2.29+.
- safe-linking (mangled fd) — 2.32+.
- large-bin size ordering checks — 2.30+.

The exploit's technique must clear the checks on ITS path — the abort
message names the failed one.
