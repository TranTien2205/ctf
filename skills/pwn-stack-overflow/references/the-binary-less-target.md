# The binary-less target — black-box only


Sometimes there's no local binary — only a service. Triage is remote:
infer protections from behavior, the cyclic from the crash signature.

## The method

- Send growing lengths; the length where it crashes bounds the buffer.
- Send the cyclic; a crash signature gives the offset via the response
  or the disconnect behavior.
- Infer protections from the crash type (canary trip vs clean RIP).

## Falsifier

The remote gives no crash signature distinguishable from a normal
disconnect — the offset can't be measured remotely; need a leak or a
different signal.
