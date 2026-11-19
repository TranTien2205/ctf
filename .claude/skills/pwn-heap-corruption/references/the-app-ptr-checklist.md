# App-owned function pointers — the no-libc target — checklist

Companion to `the-app-ptr.md`.

## Checklist

- [ ] Source: struct fields called later.
- [ ] r2 -A: afl for indirect-call candidates; axt on function pointers.
- [ ] A "run/execute/print" menu op that dispatches through a field.
