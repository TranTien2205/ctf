# Seed-search deep — when the seed is the whole attack

## The premise

No state recovery needed if the seed is enumerable. `random.seed(int(time()))`,
`srand(time(0))`, `mt_srand(time())`, `new Random(System.currentTimeMillis())`,
`random.seed(pid)` — the seed space is small enough to brute-force.

## The window bound — the whole skill

Enumerate only if the window is BOUNDED. Sources of the bound:

- **The issue epoch** — `issued_at`/`iat`/`created` in the token/artifact
  → the seed ∈ `[issue - slack, issue + slack]`.
- **The request time** — you know when you asked → narrow window.
- **pid range** — `0..32768` typical → enumerable alone.
- **Second vs ms vs ns** — `time()` (sec), `time()*1000` (ms — 1000× more),
  `time_ns` (ns — usually too big unless the window is tiny).

## The platform seeds cheat sheet

| Generator | Seed shape | Window |
|---|---|---|
| `random.seed(int(time()))` | epoch sec | `±slack` |
| `mt_srand(time())` (PHP) | epoch sec | `±slack` |
| `srand(time(0))` (C) | epoch sec | `±slack` |
| `new Random(currentTimeMillis)` | epoch ms | `±slack*1000` |
| `random.seed(pid)` | pid | `0..32768` |
| `random.seed(pid ^ int(time()))` | two-factor | bound both |

## The search pattern

```python
import random
target = observed_output
for ts in range(lo, hi):
    r = random.Random(ts)          # or the platform's generator
    if r.getrandbits(32) == target: # or .random(), .randint, the right call
        seed = ts
        break
# then r.<the same call> predicts the NEXT output
```

- The clone must reproduce the SAME call — `getrandbits(32)`, `random()`,
  `randint` differ in which internal words they consume.
- For `mt_srand`/`rand`/`java.util.Random`, reimplement the generator or
  use the platform's — Python's `random` is MT19937 but PHP `mt_rand` and
  `java.util.Random` are different algorithms.

## The two-factor seed

`seed = pid ^ int(time())` — enumerate `pid` × `time` (32k × window) —
still bounded if the window is small. Cross-product, compare.

## The CSPRNG boundary

`seed = os.urandom`/`secrets.token_bytes`/`/dev/urandom` — NOT enumerable
→ the whole family is out → reclassify (`class-boundary.md`). The check:
is the seed a small function of time/pid, or an entropy source?

## Expected signal / falsifier

- **Expected signal**: a seed that reproduces the observed output, then
  predicts the next.
- **Falsifier**: no seed in the window reproduces the output → widen the
  bound or the generator is different / CSPRNG.
