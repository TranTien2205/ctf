# Identifying the libc version — the fingerprint — checklist

Companion to `the-version-id.md`.

## Checklist

- [ ] 1. Leak 2-3 resolved imports' addresses.
- [ ] 2. Their pairwise distances fingerprint the libc build.
- [ ] 3. tools/gadget_lookup.py --lockfile or a libc database matches.
