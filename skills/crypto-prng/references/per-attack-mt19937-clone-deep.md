# per-attack mt19937-clone deep — the 624-word clone

## The command

```bash
python3 tools/crypto_attack.py mt19937-clone --outputs o0,...,o623 [--count n]
python3 tools/crypto_attack.py mt19937-clone --outputs-file f [--count n]
```

Exactly 624 consecutive raw `getrandbits(32)` words.

## The math

`temper` is a fixed invertible 4-step shift/XOR mask:

```
y ^= y>>11; y ^= (y<<7)&0x9D2C5680; y ^= (y<<15)&0xEFC60000; y ^= y>>18
```

`untemper` inverts it bit-by-bit. `untemper` each of 624 consecutive
words → the full state array → `predict_next` rolls the twist forward.

## The four requirements — all mandatory

1. **624** — the whole state array. `<624` → no clone.
2. **consecutive** — index 0..623, no gap.
3. **raw** — `getrandbits(32)`, NOT `random()`/`randint`/`choice`/
   `getrandbits(k<32)`.
4. **no reseed** — same generator, no `seed()` in the window.

## The output-shape traps — the most common failure

- **`random()`** — a `getrandbits(53)` pair → two words per float, not a
  32-bit word.
- **`randint(a,b)`/`choice`/`shuffle`** — post-processed.
- **`getrandbits(k)`, k<32** — truncated word.
- **a shared `random` module** — other callers inject gaps.
- **`seed()` per request** — each request a fresh generator.

## The `--count` flag

`--count n` emits the `n` outputs AFTER the 624 — predictions. For the
next token/roll, `--count 1` and verify against the held-back word.

## The seed-search fallback

`<624` → the clone can't run. `seed=time()`/`pid` → the seed-search
branch instead — enumerate the window, match, clone from the seed.

## The `mt_rand`/`numpy` variant

PHP `mt_rand` / `numpy.random` / `std::mt19937` — same MT core, different
SEEDING and output handling — a Python `random` clone on them fails.
Fingerprint the variant.

## The verification

`o0..o623` recover, `o624` held back → `predict == o624`.

## Expected signal / falsifier

- **Expected**: `predict == held` word.
- **Falsifier**: `predict != held` → <624/non-raw/gap/reseed/variant.
