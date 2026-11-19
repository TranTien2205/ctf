# mt19937-clone deep — the Mersenne Twister clone

## The attack id

```bash
python3 tools/crypto_attack.py mt19937-clone --outputs o0,...,o623
python3 tools/crypto_attack.py mt19937-clone --outputs-file outs.txt
python3 tools/crypto_attack.py mt19937-clone --outputs-file outs.txt --count 10
```

`--outputs` = comma-separated raw 32-bit words, or `--outputs-file` a
file. `--count n` = emit the next `n` outputs.

## The math

MT19937's `temper` is a fixed sequence of four invertible shift/XOR masks:

```
y ^= y >> 11
y ^= (y << 7) & 0x9D2C5680
y ^= (y << 15) & 0xEFC60000
y ^= y >> 18
```

Each step is a GF(2)-linear bijection on 32 bits — `untemper` inverts it
by working bit-by-bit from the top/bottom. Feed 624 consecutive tempered
words → `untemper` each → the full internal state array → the generator
is cloned.

## The four requirements — all mandatory

1. **624 outputs** — the whole state array. 623 → one word missing → no
   clone.
2. **consecutive** — every word from index 0 to 623, no gap. A shared
   `random` module consumed elsewhere injects gaps → the window is off.
3. **raw words** — `getrandbits(32)` exactly. NOT `random()`, NOT
   `randint`, NOT `choice`, NOT `getrandbits(k<32)`.
4. **no reseed** — `random.seed()` inside the window resets the index →
   the collected words span two different streams.

## The output-shape traps — the most common failure

- **`random.random()`** — a float = `getrandbits(53)/2^53`, consuming TWO
  words and returning neither raw. Do not clone on floats.
- **`randint(a,b)` / `choice(seq)` / `shuffle`** — post-processed words.
- **`getrandbits(k)`, k<32** — a truncated word; the low bits are dropped.
- **a reseed per request** — `random.seed(time())` in the handler → each
  request a fresh generator → seed-search, not clone.

## The `--count` flag

`--count n` emits `n` outputs AFTER the 624 — i.e. predictions. For the
next token/roll, `--count 1` and verify against the held-back output.

## The seed-search fallback

<624 → the clone can't run. If the seed is small (`time()`/`pid`), the
attack becomes `per-family-seed` — enumerate the seed window, match an
output, clone from the matched seed.

## The verification

Collect 625 outputs: `o0..o623` recover, `o624` held back. `predict ==
o624` is the only accept.

## The chain

`mt19937-clone` → `predict_next` → the admin's session id / next token /
next roll → the flag-object.

## Expected signal / falsifier

- **Expected signal**: `predict == held-back` word.
- **Falsifier**: `predict != held` → <624, non-consecutive, non-raw, or a
  reseed in the window. Re-collect / switch to seed-search.
