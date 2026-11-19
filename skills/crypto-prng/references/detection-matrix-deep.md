# Detection matrix deep — every observation, ranked by discrimination power

## The fingerprint order — most discriminating first

A fingerprint is a cheap test that names the generator family. Run the
most discriminating test first — one hit routes the whole solve.

### 1. The generator name — a free fingerprint

`mt19937`/`xorshift`/`LFSR`/`LCG`/`rand`/`mt_rand`/`getrandbits` in source
or comments. The strongest signal — if the generator is named, skip the
statistical tests and go straight to the count gate.

### 2. The output shape — structural

| Shape | Points to | Power |
|---|---|---|
| 624+ raw 32-bit words | MT19937 | high — the count is the giveaway |
| a bitstream | LFSR | high — only LFSR emits bits natively |
| 4+ raw 32-bit words | xorshift/MT | medium — count separates them |
| mod-`m` ints | LCG | medium — the modulus structure |
| floats in `[0,1)` | MT/random() variant | low — post-processed |
| time-like (changes per second) | seed-search | medium |

### 3. The LCG test — the difference gcd

```
t_i = x_{i+1} - x_i
m_candidate = gcd over i of (t_{i+1}·t_{i-1} - t_i^2)
```

A nonzero stable `m` → an affine structure → LCG. A gcd collapsing to 0/1
→ not affine → not an LCG. Cheap, high power on LCG streams.

### 4. The LFSR test — Berlekamp-Massey

Run BM on the bits. A small convergent linear complexity `L` → an LFSR of
width `L`. `L ≈ n/2` → not a plain LFSR. The test IS the attack's first
step — a positive result IS the recovery's start.

### 5. The MT test — the 624-count clone

Collect ≥624 raw words, try `mt19937-clone`. `predict == held` → MT. The
clone itself is the fingerprint — expensive but decisive.

### 6. The seed test — the window bound

`seed = time()`/`pid` visible in source, or outputs that change
per-second/per-request → bound the window → enumerate → match. The
fingerprint is the seed's shape, not the output statistics.

## The generator table — the full discriminator

| Generator | State | Output | Count | Attack |
|---|---|---|---|---|
| LCG `a·x+c mod m` | log2 m | x / x>>b / x mod n | 3/6/required | `lcg-*` |
| LFSR w taps t | w | 1 bit | 2w | `berlekamp`/`lfsr-*` |
| MT19937 | 19968 | 32-bit word | 624 | `mt19937-clone` |
| xorshift128 | 128 | 32-bit w | 4 | `xorshift128` |
| seed(time) | ~log2 window | generator's | window | seed-search |
| CSPRNG | large | large | none | out of class |

## The negative-power tests — don't rely on these

- **uniformity** — all PRNGs look uniform; no discrimination.
- **bit randomness** — `rand` and `urandom` both look random.
- **a single output's value** — says nothing.
- **"it looks random"** — the whole class is "looks random but isn't".

## The discrimination rule

Structure over statistics. The outputs' SHAPE (count, width, bit vs word,
time-coupling) names the generator faster than any statistical test.
