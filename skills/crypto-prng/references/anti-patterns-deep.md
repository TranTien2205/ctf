# Anti-patterns deep — the behaviors that burn budget without progress

## The payload-variation loop

Re-running `mt19937-clone` on the same 623 outputs with a different
`--count` — the count is the gate; no `--count` recovers a 624th word.
The fix is MORE outputs, not another flag.

## The flag-fiddling loop

- `lcg-truncated --low-bits 31` fails → `--low-bits 32` fails →
  `--low-bits 33`... — a wrong `--low-bits` is wrong in either direction;
  recount the DROPPED bits from the source's `x >> b`, don't guess.
- `lfsr-predict --taps [16,14,13,11]` fails → try `[16,15,13,4]`... —
  don't guess taps; run `berlekamp-massey` to derive them.

## The same-mechanism mutation

Trying a "different" `lcg-recover` flag set when the underlying model
(`x mod n` instead of `x`) is wrong — every run returns wrong `a`,`c` for
the same reason. The failure is the MODEL, not the flag. Fix the
normalization, not the command.

## The stat-fishing loop

- "the outputs look uniform so maybe MT" — uniformity is not a
  fingerprint; run the structural tests.
- "let me try every generator" — fingerprint first; the shape names the
  family.

## The ignore-the-falsifier loop

`predict != held` → "maybe one more output" — a `predict` that fails on
held-back data has FALSIFIED the recovery; more outputs won't verify a
wrong model. Record the falsifier, change the mechanism.

## The skip-verification shortcut

- recording `a`,`c`,`m` from a return value without `predict==held`.
- matching `predict` to a training output and calling it verified.
- one lucky match = a recovery.
- recording a `flag{`-shaped string from the description.

## The wrong-class persistence

- running `lcg-*`/`lfsr-*`/`mt-*` on a CSPRNG/`urandom`/`secrets` stream
  because "it's still random outputs" — the gcd/BM/clone will all
  falsify; the class is wrong. Reclassify.
- running `mt19937-clone` on a `random.seed(time())` oracle — it's
  seed-search, not clone.

## The unbounded-seed enumeration

Enumerating `seed` without bounding the window — a 2^31 or ms/ns window
is not enumerable. Bound it from the issue epoch FIRST; if it can't be
bounded, it's not seed-search.

## The convention-confusion loop

Flipping `--low-bits` and `--taps` conventions randomly instead of
reading which indexing the tool uses. Read the `--help`; fix ONE
convention, verify, THEN suspect another.

## The budget-burn pattern

5+ probes on the same mechanism class (same generator, same model) → the
controller counts. A falsifier that fires ends the mechanism — record it
in `attempts/` and let `decide.py` pick the next rung, instead of a 6th
variant.
