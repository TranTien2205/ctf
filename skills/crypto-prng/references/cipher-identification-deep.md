# Cipher identification deep — which generator is this stream?

## The identification problem

The output stream is the only evidence — no source names the generator.
Identify it from the stream's structure.

## The bit-vs-word split — the first discriminator

- **A bitstream** (0/1 outputs) → LFSR or a bit-level generator. Only
  LFSR-family emits bits natively.
- **A word stream** (ints/32-bit) → LCG, MT, xorshift, or a seeded
  generator.

## The bitstream branch — LFSR

- Run Berlekamp-Massey. `L` convergent & « n → LFSR(width=L). `L ≈ n/2`
  → combiner/non-LFSR.
- The stream's `0/1` density ~50% — not discriminating; the linear
  complexity is.

## The word-stream branch — the sub-split

### `x mod m`-sized ints → LCG

- Difference gcd: `gcd(t_{i+1}t_{i-1}-t_i^2)` → stable `m` → LCG.
- `m` a power of 2 or 2^31/2^48 → glibc/java/standard LCG.

### 32-bit words, many → MT or xorshift

- 624+ → `mt19937-clone` test.
- 4-623 → `xorshift128` test (4 words pin it) or seed-search.
- `predict==held` on the clone/inversion → that's the generator.

### Floats `[0,1)` → `random()`/`Math.random`

- `random()` = MT `getrandbits(53)` pair → the underlying words.
- `Math.random` = `xorshift128+` + double — a different variant.
- `mt_rand`/`java.util.Random`/`drand48` — the platform LCG variants.

### A time-coupled value → seed-search

- Outputs that change per second/per request → `seed=time()`/`pid`.

## The keyed/secure boundary — out of class

- `os.urandom`/`secrets`/`crypto.`/`SecureRandom`/`arc4random`/`hash`/HMAC
  — CSPRNG or keyed → no recovery → `crypto-symmetric-oracle` or out.

## The identification table

| Stream looks like | Test | Result |
|---|---|---|
| bits | BM | `L` small → LFSR |
| mod-m ints | gcd | stable m → LCG |
| 624 words | clone | `predict==held` → MT |
| 4 words | invert | `predict==held` → xorshift |
| floats | the pair | `random()`/`128+` |
| time-coupled | bound | seed-search |
| none fit | — | CSPRNG → out |

## The dual-naming trap

`rand()` is glibc-additive (not LCG); `random()` is Python MT (not
xorshift); `mt_rand` is PHP MT (not Python MT); `Math.random` is V8
`xorshift128+`. The NAME doesn't name the algorithm — fingerprint the
structure.
