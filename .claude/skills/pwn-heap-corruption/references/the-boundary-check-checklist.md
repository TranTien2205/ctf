# The boundary check — which writes can reach — checklist

Companion to `the-boundary-check.md`.

## Checklist

- [ ] A data-only write (inside the object's buffer) can't corrupt
- [ ] An index-OOB reaches neighboring globals — different targets.
