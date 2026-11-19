# The remote libc — matching the build — checklist

Companion to `the-remote-libc.md`.

## Checklist

- [ ] 1. Leak TWO resolved imports (puts + printf, say).
- [ ] 2. Their distance fingerprints the build.
- [ ] 3. Name the version; derive every offset from it.
- [ ] The shipped libc file (exact).
- [ ] The fingerprint db (tools/gadget_lookup.py or a libc db).
