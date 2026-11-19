# tcache count — faking occupancy — checklist

Companion to `the-count-field.md`.

## Checklist

- [ ] 1. The struct sits at heap_base+0x10 (first alloc's chunk).
- [ ] 2. Write count[k] = 7 → the bin reads full → later frees route
- [ ] 3. Or set count[k] = 1 with a fake entry pointer → alloc returns the
