# Leaking the canary — the prerequisite — checklist

Companion to `the-canary-leak.md`.

## Checklist

- [ ] A format-string read of the canary's slot.
- [ ] An info-disclosure bug reading stack data.
- [ ] Brute-force on a fork-server (the canary is per-process, constant
