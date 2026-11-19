# The first failure — bisecting the chain — checklist

Companion to `the-first-fail.md`.

## Checklist

- [ ] Break at the overwrite point; step.
- [ ] If gadget 1 doesn't execute: the overwrite missed — re-measure the
- [ ] If gadget N misbehaves: its side effects — audit the tail.
- [ ] If the call crashes: alignment or a bad target.
