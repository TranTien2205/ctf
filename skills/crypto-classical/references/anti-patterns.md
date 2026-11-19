# Anti-patterns — the habits that cost a solve

## Skipping the identify

A `subst` anneal on a `vigenere` — `cipher_id` first: the IC (~0.066 vs ~0.038)
and Kasiski settle it in one read.

## Re-running a falsified family

No `k`/`L`/language → the family closes — *change family*, don't re-run with
the same input.

## The cipher-vs-encoding confusion

`+/=`/hex/`01` → `enc_detect` — a *base64* `ct` annealed as `subst` is a wasted
probe. The charset is the discriminator.

## The short-ct over-trust

Under ~30 chars the IC/chi²/Kasiski are unreliable — a 15-char `ct` with IC 0.04
is not a `vigenere`. The `flag{` positions and common letters carry the solve.

## The near-decode as the flag

`gLAG{...}` / `fLAG{...}` — a partially-right `σ`. The `flag{` positions reveal
the wrong `σ` entries — swap them. A near-decode is a *candidate*.

## The layered re-attack

A decode that yields another `ct` — a *new* `ct` — `cipher_id` on the output,
not a re-run of the first layer's solve.

## The named-cipher blind spot

A name in the text — "we used a playfair cipher" — no `classical_solve` covers
it. `other-ciphers.md` → a script / dcode.fr.

## The unverified verify

"it looks like English" — `enc(pt) == ct` is the verify; a plausible read
without the re-encrypt isn't confirmed.
