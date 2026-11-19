# Cipher identification — which generator emitted this stream

## The split

- **bits** → LFSR. **words/ints** → LCG/MT/xorshift. **floats** →
  `random()`/`Math.random`. **time-coupled** → seed-search.

## The word-gen sub-split

- `mod-m` ints → LCG (gcd the differences).
- 624+ raw `getrandbits(32)` → MT (`mt19937-clone`).
- 4 raw words → xorshift (`xorshift128`).
- bounded seed → seed-search.

## The platform variants

- `mt_rand` (PHP) → MT variant, different seeding.
- `java.util.Random` → 48-bit LCG, `nextInt`=`x>>16`.
- `Math.random` (V8) → `xorshift128+` — NOT `xorshift128`.
- `glibc rand()` → additive, not plain LCG.
- `drand48`/`lrand48` → `lcg-truncated`, `low-bits=16/17`.

## The boundary

- `os.urandom`/`secrets`/keyed → out of class.
- a decode (base64/hex) yielding structure → encoding-carrier.

## The fingerprint command map

| Suspect | Test |
|---|---|
| LCG | `gcd` diffs → `m` |
| LFSR | `berlekamp-massey --bits` |
| MT | `mt19937-clone --outputs` |
| xorshift | `xorshift128 --outs` |
| seed | `random.seed(ts)` loop |
