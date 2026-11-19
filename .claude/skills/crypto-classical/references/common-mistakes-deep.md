# Common mistakes deep — the errors, annotated

## Treating an encoding as a cipher

`+/=`/hex/`01` `ct` → `enc_detect` — a *base64* blob annealed as `subst` is a
wasted probe. The charset is the discriminator — always the first read.

## Annealing a polyalphabetic

`subst` on a `vigenere` (IC~0.038) — the anneal can't crack it; each `ct`
position is a mix of `L` shifts. `cipher_id` first; Kasiski for `L`; then `L`
Caesars.

## Reading a near-decode as the flag

`gLAG{...}` → a partially-right `σ` — the `flag{` positions reveal the wrong
`σ` entries. Swap `σ⁻¹(g)→f` — don't submit `gLAG{...}`.

## Re-running a falsified family

No `k` produces language → `caesar` is *closed* — change family (`subst`/
transposition); don't re-run.

## The `L` mis-estimate

A near-English Vigenere with a wrong `L` — try `L`, `L/2`, `2L`; the
coset-IC confirms.

## The keyed-alphabet trap

A `subst` over a `KEYWORD` alphabet — `σ` solves it anyway; the keyword shows
in the recovered `σ` order.

## The `π(σ(p))` layered trap

A transposition *of* a substituted text — the letters aren't English.
Un-scramble `π` (position-only) *first*, then `subst` the un-scrambled.

## The unverified verify

"it looks English" — `enc(pt) == ct` is the verify; a plausible read without
the re-encrypt isn't confirmed.
