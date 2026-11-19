# Anti-patterns deep — the habits that cost the solve, annotated

## Skipping `cipher_id`

A `subst` anneal on a `vigenere` — the IC (~0.066 vs ~0.038) and Kasiski
settle it in *one read*. The statistics are cheap; the anneal isn't.

## Re-running a falsified family

No `k`/`L`/language → the family closes — *change family*, don't re-run. A
falsifier is a signal, not a suggestion to try harder.

## The cipher-vs-encoding confusion

`+/=`/hex/`01` → `enc_detect` — a `base64` `ct` annealed as `subst` is a
wasted probe. The charset is the *first* read.

## The short-ct over-trust

Under ~30 chars the IC/chi²/Kasiski are unreliable — a 15-char `ct` with IC
0.04 is not a `vigenere`. The `flag{`/`CTF{` positions and common letters
carry the solve.

## The near-decode as the flag

`gLAG{...}` / `fLAG{...}` — a partially-right `σ`. The `flag{` positions reveal
the wrong `σ` entries — swap them. A near-decode is a *candidate*.

## The layered re-attack

A decode that yields another `ct` — a *new* `ct` — `cipher_id` on the output,
not a re-run of the first layer's solve.

## The named-cipher blind spot

"we used a playfair cipher" — `classical_solve` doesn't cover it —
`other-ciphers.md` → a script / dcode.fr.

## The unverified verify

"it looks like English" — `enc(pt) == ct` is the verify.
