# Per-family seed — the timestamp/weak-seed branch

## The shape

`random.seed(time())`, `srand(time(0))`, `mt_rand(ts)`, `random.seed(pid)`,
`new Random(System.currentTimeMillis())` — the state IS a small guessable
value, not a recoverable-from-outputs one.

## The discriminator

```
seeded by time()/pid/small-int?  → seed-search (enumerate the window)
generator state recoverable?     → the lcg/lfsr/mt attacks
```

## The attack — enumeration, not recovery

```python
import random, time
for ts in range(lo, hi):           # the seed window
    r = random.Random(ts)
    if r.getrandbits(32) == first_observed:
        # ts is the seed — predict forward
```

## The window bound

- `time()` → bound `[event_start - slack, now + slack]` — the challenge's
  stated epoch.
- `getpid()` → the pid range (≤ 2^15/2^22).
- `rand()%N` → the seed's low bits.

## The invariants

- The state isn't recovered — the SEED is brute-forced against an observed
  output.
- The window must be bounded or the search is unbounded → falsifier.

## The verify

A seed whose generator reproduces the observed outputs bit-for-bit.

## The boundary

If the seed is `os.urandom`/`secrets`/CSPRNG → not enumerable → NOT this
class (`class-boundary.md`).
