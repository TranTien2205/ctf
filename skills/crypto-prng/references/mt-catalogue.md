# MT / xorshift catalogue — the word-stream generators, indexed

## The attack ids

| Id | Generator | Leak | Count | Tool |
|---|---|---|---|---|
| `mt19937-clone` | MT19937 | 32-bit words | 624 | `crypto_attack.py mt19937-clone` |
| `xorshift128` | xorshift128 | 32-bit words | 4 | `tools/crypto/xorshift128.py` |

## MT19937 — the details

- **state** 19968 bits (624×32 words); `G`=`temper` (invertible).
- **count** exactly 624 consecutive raw `getrandbits(32)` words.
- **falsifier** `predict!=held` → <624/non-raw/gap/reseed/variant.

### The MT variants

| Variant | Status |
|---|---|
| Python `random` | covered |
| PHP `mt_rand`/`mt_srand` | different seeding/mode |
| C++ `std::mt19937` | same core, different seed |
| `numpy.random` | MT or PCG64 — fingerprint |

## xorshift128 — the details

- **state** 128 bits (4×32 words); `G`=`w` (the whole word).
- **count** exactly 4 consecutive words.
- **falsifier** `predict!=held` → wrong variant/non-consecutive.

### The xorshift variants

| Variant | Status |
|---|---|
| `xorshift128` | covered |
| `xorshift128+` (V8 `Math.random`) | NOT covered — `+` variant |
| `xorshift64*` | NOT covered |
| `xoroshiro`/`xoshiro` | NOT covered |

## The shared gates

- raw words only — `random()`/`randint`/`Math.random` normalize/variant.
- consecutive — no gap, no reseed.
- `predict == held` — the accept.

## The discriminator

| Count + shape | Route |
|---|---|
| 624 raw words | `mt19937-clone` |
| 4 raw words | `xorshift128` |
| <624 + small seed | seed-search |
| floats | `random()`/`128+` variant |
