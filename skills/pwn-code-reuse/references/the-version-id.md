# Identifying the libc version — the fingerprint


A leaked address identifies the libc version by symbol-offset
fingerprint: two or three known symbol distances pin the build.

## The method

1. Leak 2-3 resolved imports' addresses.
2. Their pairwise distances fingerprint the libc build.
3. tools/gadget_lookup.py --lockfile or a libc database matches.

## Falsifier

The fingerprint matches nothing known: compute offsets from the
shipped libc file or fall back to version-tolerant techniques.
