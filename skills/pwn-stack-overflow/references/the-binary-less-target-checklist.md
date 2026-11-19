# The binary-less target — black-box only — checklist

Companion to `the-binary-less-target.md`.

## Checklist

- [ ] Sometimes there's no local binary — only a service. Triage is remote:
- [ ] infer protections from behavior, the cyclic from the crash signature.
- [ ] Send growing lengths; the length where it crashes bounds the buffer.
- [ ] Send the cyclic; a crash signature gives the offset via the response
- [ ] or the disconnect behavior.
- [ ] Infer protections from the crash type (canary trip vs clean RIP).
- [ ] The remote gives no crash signature distinguishable from a normal
- [ ] disconnect — the offset can't be measured remotely; need a leak or a
- [ ] different signal.
