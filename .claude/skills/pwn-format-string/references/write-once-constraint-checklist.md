# One write per call — the shot budget — checklist

Companion to `write-once-constraint.md`.

## Checklist

- [ ] 1. In one call: all %n writes execute in order — compose multi-target
- [ ] 2. The cumulative count constraint applies within the call.
- [ ] 3. A re-triggerable service gives more shots.
