# per-attack berlekamp-massey deep — the recurrence recovery

## The command

```bash
python3 tools/crypto_attack.py berlekamp-massey --bits 0,1,1,0,...
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex <hex>
python3 tools/crypto_attack.py berlekamp-massey --bits-file f
```

Exactly one input form. Returns `(width, taps)` — the minimal LFSR.

## The algorithm

Berlekamp-Massey scans the bitstream once, maintaining a candidate
connection polynomial `C(x)`. On a discrepancy it updates `C` and the
span `L`. For a width-`w` LFSR, `2w` bits converge to the true `C`.

## The `L` output — the gate

`L` (linear complexity) = the minimal LFSR width.

- `L` small and convergent (stops growing with more bits) → a real LFSR
  of width `L` → proceed to `lfsr-recover`/`lfsr-predict`.
- `L ≈ n/2` and grows with `n` → the stream is NOT a plain LFSR — a
  combiner, a filtered LFSR, or a CSPRNG stream → the falsifier.

## The count floor

`2·w` bits. Below → underdetermined — multiple recurrences fit the
prefix → the returned `taps` may be wrong even if `L` looks small.

## The input-form gotchas

- `--bits` — comma `0,1,...`. A `0101` STRING is wrong — it wants commas.
- `--keystream-hex` — the hex unpacks to bits; the per-byte bit ORDER
  matters — `deadbeef` MSB-first vs LSB-first gives two streams; if the
  recovered `w`/`taps` fail, flip the order.
- `--bits-file` — a file of bits.

## The `(w,taps)` → predict chain

```
berlekamp-massey --bits <s>  →  (w, taps)
→ lfsr-recover --bits <s> --width w   →  register (or confirm taps)
→ lfsr-predict --bits <s> --taps <taps> --width w --count n  →  future
```

## The combiner falsifier

An NLF/combiner output — `f(LFSR_1,...,LFSR_k)` — has linear complexity
≈ the product of widths → `L ≈ n/2` → BM can't recover → the falsifier →
correlation attack (out of this module).

## Expected signal / falsifier

- **Expected**: `(w,taps)`, `L` « n, `lfsr-predict` on it reproduces
  held-back bits.
- **Falsifier**: `L ≈ n/2` or predicted diverges → not a plain LFSR.
