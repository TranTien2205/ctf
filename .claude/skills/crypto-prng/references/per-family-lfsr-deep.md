# Per-family LFSR deep — the bit-stream generator, every variant

## The family

A width-`w` register over GF(2); each clock emits the end bit and shifts
in `XOR(tap bits)`. The whole future is `w` bits + the tap polynomial.
Every LFSR attack is "get the taps (if unknown), get the register, roll
forward".

## The three attacks — the decision

| Known | Have | Attack |
|---|---|---|
| taps | bits | `lfsr-predict --count n` |
| width only | bits | `lfsr-recover --width w` |
| nothing | bits | `berlekamp-massey` → taps+width |

The "taps known?" column IS the discriminator.

## `berlekamp-massey` — recover the taps

≥`2w` bits → the minimal recurrence → `(width, taps)`. The linear
complexity `L` is the gate: `L` convergent and « n → a real LFSR;
`L ≈ n/2` → a combiner/non-LFSR (falsifier).

## `lfsr-recover` — get the register

`--bits` + `--width` (taps optional, BM-derived) → `(register, taps,
width)`. The register is the last `w` bits.

## `lfsr-predict` — roll forward

`--bits --taps --width --count n` → the next `n` bits. `lfsr-predict` is
the close — it consumes the `(taps, width)` the recovery produced.

## The tap convention — the trap that always bites

`--taps` is **1-indexed from the LSB** (the output end). A polynomial
`x^16+x^14+x^13+x^11+1` in a writeup indexes from the MSB or by degree —
a direct transcription to `--taps` gives a mirrored polynomial →
`predict` diverges. Re-index: for a width-`w` LFSR, a degree-`d` tap maps
to position `w-d` (check the tool's convention with a known stream).

## The stream-cipher shape — the common challenge

`ct = pt ⊕ keystream`. A known `pt` prefix (`flag{`) yields the first
keystream bits → BM → `lfsr-predict --count` → the rest of the keystream
→ `ct ⊕ ks` → flag. The known-plaintext is the entry.

## The combiner boundary — the falsifier's home

Real stream ciphers combine `k` LFSRs with a nonlinear `f` — the output's
linear complexity is ~the product of the widths, so BM returns `L ≈ n/2`.
That's the falsifier — the attack is then a **correlation attack**
(isolate each LFSR by its correlation to the output) — out of this
module's scope. `L` « `n/2` = plain LFSR; `L ≈ n/2` = combiner.

## The variants

- **Fibonacci LFSR** — the standard XOR-taps-in form; what the tools model.
- **Galois LFSR** — the XOR applies to the register contents, not just the
  new bit — a different but equivalent recurrence; BM still works on the
  output bits.
- **shrinking/self-shrinking** — irregular clocking — high complexity →
  the falsifier.

## The verification

`lfsr-predict --count k` vs `k` held-back bits — `predict == held`.
