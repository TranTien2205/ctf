# Common mistakes — the errors that cost the solve

## Treating an encoding as a cipher

`+/=`/hex/`01` `ct` → `enc_detect` — not a `subst`. The charset is the
discriminator.

## Annealing a polyalphabetic

`subst` on a `vigenere` (IC~0.038) — the anneal can't crack it. `cipher_id`
first; Kasiski for `L`.

## Reading a near-decode as the flag

`gLAG{...}` → the `flag{` positions reveal the wrong `σ` entries — polish, not
a flag.

## Re-running a falsified family

No `k` produces language → the `caesar` is *closed* — change family; don't
re-run.

## The `L` mis-estimate

A near-English Vigenere with a wrong `L` — try `L`, `L/2`, `2L`; the coset-IC
confirms.

## The keyed-alphabet trap

A `subst` over a `KEYWORD` alphabet — `σ` still solves it; the keyword shows
in the recovered `σ` order.

## The transposition-of-substitution

`π(σ(p))` — the letters aren't English — un-scramble `π` first (position-only),
then `subst`.

## The unverified verify

"it looks English" — `enc(pt) == ct` is the verify.
