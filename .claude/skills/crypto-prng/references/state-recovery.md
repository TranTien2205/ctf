# PRNG state recovery

"Random" in a CTF is almost always one of three generators, and each fails a
different way. Identify the generator first — the recovery math follows from
that, not the other way around.

## Identify the generator

| Symptom in the handout | Generator | The break |
|---|---|---|
| `random`/`getrandbits` Python, Mersenne words | MT19937 | 624 outputs → clone state |
| `rand()%N`, `srand(time)` C, `Random` Java/.NET | LCG / libc rand | 3-4 outputs → solve a,b,m |
| `Math.random`, `random.seed(time)` | seeded from time | brute the seed window |
| `os.urandom`, `secrets`, CSPRNG named | real randomness | not this class — bug is elsewhere |

## MT19937 (the common CTF one)

Needs 624 consecutive 32-bit outputs — usually `getrandbits(32)` or
`random()` collected sequentially:

```python
from mt19937predictor import MT19937Predictor   # pip install mt19937predictor
p = MT19937Predictor()
for out in observed_624:
    p.setrandbits(out, 32)
assert p.getrandbits(32) == next_real_output
```

Variants to try when the count is short: `random()` floats give 53 bits each —
two `random()` calls reconstruct two state words. Partial outputs (tokens,
otps, truncated hex) need `untwister`-style symbolic recovery, harder — grab
more outputs first.

## LCG / libc rand

`x_{n+1} = (a·x_n + b) mod m`. With `m=2^31` (glibc) or `m=2^32` (MSVC), three
outputs solve `a`, `b` if unknown; with known constants (glibc: `a=1103515245,
b=12345`), one seed guess is enough — brute `srand(seed)` over a plausible
`time()` window.

## Seeded-from-time

`seed(time())`, `srand(time(0))`, or a timestamp-derived key: brute a window
around the observation time — ±minutes if you know when the token minted,
wider if not. The signal to record: the *width* of the window you brute, not
"it was seeded badly".

## Truncated / combined outputs

When the output is `rand() % N`, `hex(token)[:8]`, or two rand values XORed —
the state is still recoverable but the math is the tool's problem: try
`mt19937predictor` with partial-bit `setrandbits` first, escalate to a z3/SMT
model only when the simple path fails.

## Falsifier

The values are `os.urandom`-sourced or a real CSPRNG, and no seed/state
leaks — prediction is impossible; the bug is in *how* the value is used
(reuse, visible comparison, bounded space), not the generator.

## Traps

- Outputs must be *consecutive* — a skipped rand() desyncs the clone; record
  every call order.
- `getrandbits(64)` consumes two state words; mixing bit-widths mid-stream
  shifts the index.
- Seed brute needs the *server's* clock, not yours — estimate from a
  `Date` header or a token timestamp first.
