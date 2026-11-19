# Confirming partial RELRO before the GOT write — checklist

Companion to `fmtstr-partial-relro-check.md`.

## Checklist

- [ ] 1. python3 tools/pwn_triage.py ./chal — the RELRO line.
- [ ] 2. Partial: GOT stays writable — %n-to-GOT works.
- [ ] 3. Full: GOT readonly — the write crashes; use ret-addr/hook instead.
