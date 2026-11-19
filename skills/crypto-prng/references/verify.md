# Verify — the proof checks

## The universal check

```python
assert predict_next == held_back_output   # bit-for-bit
```

Every attack's verify is the same: reproduce a value held back from the
recovery. One matching output is a coincidence; a sequence is a recovery.

## The per-attack verify

| Attack | Verify |
|---|---|
| `lcg-*` | `a`,`c`,`m` → `next = a·x+c mod m` matches held-back |
| `lfsr-*` | predicted `n` bits match the next keystream window |
| `mt19937-clone` | `predict_next` matches held-back word(s) |
| `xorshift128` | `--predict` matches held-back outputs |
| seed-search | seed's generator reproduces the observed sequence |

## The honest standard

- **Bit-for-bit** — not "close", not "the right length", not uniform.
- **Held-back** — the output was NOT fed to the recovery; it's the test.
- **A sequence** — one lucky match isn't proof; two+ consecutive is.

## The flag verify

`flag{`/`CTF{` in the recovered stream, forged token accepted, or the
predicted nonce used — the `impact` step after `class` verify.

## The verify helpers

```python
# LCG
assert (a*x_last + c) % m == observed_next
# MT
assert mt19937.predict_next(state) == observed_word
# seed
assert random.Random(seed).getrandbits(32) == observed
```
