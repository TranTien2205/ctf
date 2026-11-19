# Per-family seed deep — the seed-search family, end to end

## The premise

The generator's `state_0 = init(seed)` where `seed` is small enough to
enumerate. The attack isn't an output leak — it's a search over
`state_0`.

## The seed shapes

| Seed | Source | Window size |
|---|---|---|
| `int(time())` | epoch sec | `±slack` (~10s) |
| `time()*1000` | epoch ms | `±slack*1000` |
| `time_ns()` | epoch ns | usually too big unless tight |
| `pid` | process id | `0..32768` |
| `pid ^ time` | two-factor | bound both |
| `user_id`/`counter` | small int | the range |
| `os.urandom`/`secrets` | entropy | UNBOUNDED → out |

## The bound — the whole skill

`seed ∈ [issue - slack, issue + slack]` — the issue epoch is the bound:

- `iat`/`created`/`issued_at`/`exp-issued`/`nbf` in the token/artifact.
- the request time — you know when you asked.
- the server clock skew — widen `slack` for drift.

Unbounded → not enumerable → out of class.

## The platform seeds

| Generator | Seed source | Generator to clone |
|---|---|---|
| `random.seed(int(time()))` | Python | `random.Random(ts)` |
| `mt_srand(time())` | PHP | `mt_rand` (PHP's MT — reimplement) |
| `srand(time(0))` | C | `rand` (glibc additive — reimplement) |
| `new Random(currentTimeMillis)` | Java | `java.util.Random` (48-bit LCG) |
| `Math.random`-seeded | JS | `xorshift128+` |
| `random.seed(pid)` | Python | `random.Random(pid)` |

## The reproduce-the-call rule

The cloned generator must reproduce the SAME call — `getrandbits(32)` ≠
`random()` ≠ `randint(a,b)` ≠ `choice`. Match the exact call the
challenge makes; a wrong call consumes different words and the seed won't
match.

## The search pattern

```python
import random
for ts in range(iat - slack, iat + slack):
    r = random.Random(ts)                  # the RIGHT generator
    if r.getrandbits(32) == observed:      # the RIGHT call
        seed = ts
        break
# r.<same call>() predicts the next output
```

## The two-factor seed

`seed = pid ^ int(time())` / `pid + time` — enumerate `pid` × `time`
(`32k × window`) — still bounded if the window is small. Cross-product.

## The falsifier

No seed in the window reproduces `o0` → widen the bound, fix the call, or
the generator is wrong / CSPRNG → out of class.

## The verify

The recovered `seed` must reproduce `o0` AND predict `o1` — one match is
a candidate, two is a recovery.
