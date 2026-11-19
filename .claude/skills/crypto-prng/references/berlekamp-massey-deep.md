# berlekamp-massey deep — recover the LFSR recurrence

## The attack id

```bash
python3 tools/crypto_attack.py berlekamp-massey --bits 0,1,1,0,...
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex deadbeef
python3 tools/crypto_attack.py berlekamp-massey --bits-file bits.txt
```

Exactly ONE of `--bits`, `--keystream-hex`, `--bits-file`. Output: the
connection polynomial → `(width, taps)`.

## The math

Berlekamp-Massey finds the SHORTEST linear recurrence over GF(2) that
generates the observed bitstream — i.e. the minimal LFSR. Running time is
O(L²) in the stream length; it processes the stream once, updating a
candidate polynomial whenever the discrepancy is nonzero.

For a width-`w` LFSR, `2w` consecutive bits suffice: the first `w` bits
are the state, the next `w` pin the recurrence.

## The count floor

`len(bits) ≥ 2·width`. Too few bits → BM returns a recurrence that fits
the prefix but isn't the generator (under-determined — many recurrences
fit a short prefix). More bits → the complexity converges to `w`.

## The linear-complexity signal

BM's key output is the **linear complexity** `L` — the minimal LFSR width.

- `L` small and stable (converges) → a plain LFSR of width `L`. Proceed.
- `L ≈ len(bits)/2` and grows with more bits → the stream is NOT a plain
  LFSR — it's a nonlinear combiner, a filtered LFSR, or a CSPRNG output.
  That is the falsifier.

## The input-shape traps

- **`--bits`** — comma-separated `0/1` ints. Not a hex string, not a bit
  string — `0,1,1,0`.
- **`--keystream-hex`** — a hex string; the tool unpacks to bits. The bit
  ORDER within each byte matters — if the recovered `w`,`taps` are wrong,
  flip the bit order (`[::-1]` per byte).
- **`--bits-file`** — a file of bits; one form, no comma parsing.

## The bit-order trap — the most common failure

A hex keystream unpacks MSB-first or LSB-first depending on convention —
the SAME bytes give two different bit streams, and only one is the real
LFSR output. If `lfsr-predict` on BM's `(w,taps)` fails, re-run BM on the
bit-reversed stream.

## The taps → predict chain

```
berlekamp-massey → (width, taps)
→ lfsr-predict --bits <stream> --taps <taps> --width <width> --count n
→ next n bits → verify against held-back bits
```

BM gives `(width, taps)`; `lfsr-recover`/`lfsr-predict` consume them.

## The combiner boundary

BM assumes a single LFSR. An NLF/combiner output has high linear
complexity — BM returns `L ≈ n/2`, the falsifier. Then the attack is a
correlation attack (per-LFSR isolation), not this module.

## Expected signal / falsifier

- **Expected signal**: `(width, taps)` with `L` « stream length,
  `lfsr-predict` reproduces held-back bits.
- **Falsifier**: `L ≈ n/2` / predicted bits diverge → not a plain LFSR.
