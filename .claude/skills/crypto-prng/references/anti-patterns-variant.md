# Anti-patterns variant — the loops, named

## The flag-guessing loop

`--low-bits 31`→`32`→`33`, `--taps [a]`→`[b]` — guessing conventions
instead of reading the source's `x >> b` or running `berlekamp-massey`
for the taps. Conventions are facts, not search spaces.

## The count-ignoring run

`mt19937-clone` on 623, `lcg-unknown-modulus` on 5, `xorshift128` on 3 —
the count IS the gate; the failure is structural, not the command.
Collect the missing output or pick a different attack.

## The normalization-skip

Feeding `x mod n`/floats/hex/`randint` to `lcg-recover`/`mt19937-clone` —
the model is wrong from the input; every flag is irrelevant. Normalize.

## The variant-confusion run

`xorshift128` on `Math.random`, `mt19937-clone` on `mt_rand`, Python
`random` on `java.util.Random` — the family is right but the VARIANT is
wrong. Fingerprint the variant.

## The model-mutation loop

`predict != held` → tweak `--outputs`/`--modulus`/`--count` → retry — the
MODEL is falsified (wrong `m`/variant/normalization), not the flag.
Re-fingerprint.

## The ignore-the-falsifier run

`gcd→0/1` or `L≈n/2` or `predict!=held` — the falsifier FIRED; another
output/flag won't resurrect a dead model. Record it, change mechanism.

## The verification-skip

Recording `a`,`c`,`m`/`state` from a return without `predict==held`. A
candidate, not a recovery.

## The unbounded-seed enumeration

Enumerating `seed` with no `iat`/bound — `time_ns` or a huge window is
not enumerable. Bound first; unbounded → out.

## The budget-burn

5+ probes on the same mechanism — the controller counts. A falsifier ends
the mechanism — `attempts` + `decide.py` the next rung.
