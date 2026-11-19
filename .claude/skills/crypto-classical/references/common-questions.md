# Common questions — the FAQ

## "How do I tell a Caesar from a substitution?"

`cipher_id` — a Caesar has **one deep chi² minimum** at `k` (the shift that
un-rotates `E`); a `subst` is a non-cyclic `σ`, so the chi² is **flat**. IC is
~0.066 for both.

## "How do I tell a Vigenere from a substitution?"

The **IC**: `vigenere` ~0.038 (the `L`-alphabet mix flattens), `subst` ~0.066
(the `σ` preserves it). Kasiski gives `L` for a Vigenere.

## "The IC is 0.05 — is it mono or poly?"

On a short `ct` the IC is noisy — the `flag{`/`CTF{` positions and common
letters carry the solve. Don't trust a 15-char IC.

## "The anneal gave `gLAG{...}`"

A partially-right `σ` — the `flag{` positions reveal which `σ` entries are
wrong. `σ⁻¹(g)` should be `f` — swap it.

## "It's base64-looking — is it a cipher?"

`+/=`/hex/`01` → `enc_detect` — an *encoding*, no key. The charset is the
discriminator.

## "A name is given — 'we used playfair'"

`other-ciphers.md` — `classical_solve` doesn't cover it — a script / dcode.fr.

## "The decode produced another ciphertext"

A layered cipher — `cipher_id` on the *output*, not a re-attack.

## "Is it verified?"

`enc(pt) == ct` and `pt` language — the re-encrypt is the verify.
