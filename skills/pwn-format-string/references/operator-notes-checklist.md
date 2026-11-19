# Operator notes — the lived experience — checklist

Companion to `operator-notes.md`.

## Checklist

- [ ] The %p leak is the cheapest confirm in pwn — one probe.
- [ ] The arg-offset N is the whole primitive — AAAA.%N$p finds it.
- [ ] %n writes the COUNT, not the pointer — the pointer is the arg.
- [ ] The count is cumulative — multiple %n in one call share it.
- [ ] x64's first 6 args are registers — your input is at high N.
- [ ] A blind fmtstr still writes — the redirect's effect is the oracle.
- [ ] The call-site's arg decides what the redirect calls — check it.
