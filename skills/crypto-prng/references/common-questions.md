# Common questions — the operator's FAQ

## "I have 3 outputs — which LCG attack?"

`lcg-recover` if `m` is known. `lcg-unknown-modulus` needs ≥6 — 3 is too
few. If `m` is unknown and you only have 3 → collect more.

## "I have `x mod n` outputs — which attack?"

NOT `lcg-recover`/`lcg-truncated` — `x mod n` is a REDUCED state, the
affine structure shifts each wrap. That's a different problem — the HNP
model for `mod` differs from `>>b`. Read the leak's exact form.

## "`mt19937-clone` on `random()` floats?"

No — `random()` returns `getrandbits(53)/2^53`, a FLOAT consuming two
words. The clone needs raw `getrandbits(32)` words. Collect words, or the
generator is a different variant.

## "`xorshift128` on `Math.random`?"

No — `Math.random` in V8 is `xorshift128+` + a `double` — a different
variant. `xorshift128.py` returns a wrong state.

## "`java.util.Random` — `lcg-unknown-modulus`?"

No — `m=2^48`, `a`,`c` are KNOWN. `nextInt` leaks `x>>16` → `lcg-truncated
--low-bits 16`, not `unknown-modulus`.

## "`--low-bits` = the kept bits?"

NO — `low-bits` = the DROPPED bits `b` in `x>>b`. `x>>32` on 64-bit →
`low-bits=32`. The most common operator error.

## "BM returned `L ≈ n/2`?"

Not a plain LFSR — a combiner or non-LFSR. The falsifier → correlation
attack (out of this module) or reclassify.

## "`predict != held` — do I try a different flag?"

Only if the flag was the convention error (`low-bits`/`taps`). Otherwise
the MODEL is falsified — change mechanism, don't mutate the same payload.

## "How do I verify a recovered `a`,`c`?"

`predict_next == held-back` — NEVER record `a`,`c` from a return value
alone. A wrong `a`,`c` interpolates the training data.

## "The seed is `os.urandom`?"

Out of class — `urandom`/`secrets` aren't enumerable. Reclassify.

## "I have 4 outputs — `xorshift128` or seed-search?"

`xorshift128` if they're consecutive raw words of a `xorshift128` stream;
seed-search if the seed is bounded. The fingerprint decides.
