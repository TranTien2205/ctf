# binmap — the arena's occupancy bitmap — checklist

Companion to `the-binmap.md`.

## Checklist

- [ ] Rarely needed — the fast paths don't consult it.
- [ ] On a miss path it decides whether the small/large walk even starts.
