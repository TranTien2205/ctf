# Recorded negatives — what didn't work and why


Every falsified route goes in the record so it isn't re-attempted:

- GOT write — full RELRO — the write crashes.
- __free_hook — glibc 2.36 — symbol absent.
- ret-addr — no stack leak — slot unknown.
- %s deref — arg not a pointer — crash.
- planted pointer — buffer is heap — not an arg.

## Record

    python3 tools/state.py <chal> --strategy-used reclassify

Each falsifier is a fact about THIS binary — reuse it, don't re-test it.
