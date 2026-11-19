# The tools — pwn_triage + radare2 + cyclic — checklist

Companion to `tools-for-fmt.md`.

## Checklist

- [ ] 1. pwn_triage ./chal — RELRO decides if GOT is writable.
- [ ] 2. r2 -A && pdf @ <func> — the printf call and its format position.
- [ ] 3. Find the arg offset: AAAA.%N$p sweep.
- [ ] 4. If it composes a smash, cyclic measures that offset.
