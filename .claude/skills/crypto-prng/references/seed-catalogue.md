# Seed catalogue — the seed-search shapes, indexed

## The seed shapes → window

| Seed | Window | Generator |
|---|---|---|
| `int(time())` | `±slack` sec | `random.Random(ts)` |
| `time()*1000` | `±slack*1000` | `random.Random(ts*ms)` |
| `time_ns()` | huge unless tight | usually out |
| `pid` | `0..32768` | `random.Random(pid)` |
| `pid^time`/`pid+time` | bound both | cross-product |
| `user_id`/`counter` | the range | enumerable |
| `os.urandom`/`secrets` | UNBOUNDED | OUT |

## The platform generators

| Seed source | Generator to clone |
|---|---|
| `random.seed(int(time()))` | Python `random.Random(ts)` |
| `mt_srand(time())` | PHP `mt_rand` — reimplement |
| `srand(time(0))` | glibc `rand` — additive, reimplement |
| `new Random(currentTimeMillis)` | `java.util.Random` — `m=2^48` LCG |
| `Math.random`-seeded | `xorshift128+` |

## The reproduce-the-call rule

The clone must make the SAME call — `getrandbits(32)` ≠ `random()` ≠
`randint` ≠ `choice`. A wrong call consumes different words → no match.

## The search

```python
for ts in range(iat-slack, iat+slack):
    if Random(ts).<call>() == o0: seed = ts
# verify: the seed reproduces o0 AND o1
```

## The bound sources

`iat`/`created`/`issued_at`/`exp-issued`/`nbf`/`timestamp` in the
artifact → `[issue-slack, issue+slack]`. Widen `slack` for clock skew.

## The falsifier

No seed in `[lo,hi]` reproduces `o0` → widen the bound / fix the call /
the generator is wrong / CSPRNG → out.

## The two-factor

`seed = pid ^ int(time())` — `pid` 0..32k × `time` window — bounded if
the window is small.
