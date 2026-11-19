# tcache count — faking occupancy


counts[i] in tcache_perthread_struct says how many chunks the bin holds
— writing it without real chunks fabricates occupancy.

## Steps

1. The struct sits at heap_base+0x10 (first alloc's chunk).
2. Write count[k] = 7 → the bin reads full → later frees route
   elsewhere.
3. Or set count[k] = 1 with a fake entry pointer → alloc returns the
   fake.

## Falsifier

The write can't reach the struct (heap start is out of range): counts
are honest — manipulate real chunks instead.
