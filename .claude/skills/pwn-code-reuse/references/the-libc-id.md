# Identifying the libc — the fingerprint check


A leaked symbol's offset identifies the libc build:

1. Leak two resolved imports (puts and printf, say).
2. Their distance in libc fingerprints the version.
3. tools/gadget_lookup.py or a libc db names the build.
4. All other offsets (system, /bin/sh, hooks) derive.

## Falsifier

No match: compute offsets from the shipped file if any, else a
version-tolerant technique.
