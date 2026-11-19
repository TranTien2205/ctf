# Detecting the reuse case — when this class applies — checklist

Companion to `detection.md`.

## Checklist

- [ ] A stack/format overwrite confirmed (cyclic offset verified).
- [ ] NX reported by the triage — no RWX page.
- [ ] The exploit needs actions the bug alone can't express (calls,
