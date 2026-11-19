# Common questions deep — the FAQ, annotated

## "How do I tell a Caesar from a substitution?"

`cipher_id` — a Caesar has **one deep chi² minimum** at `k` (the shift that
un-rotates `E`); a `subst` is a non-cyclic `σ`, so the chi² is **flat** — no
`k` fits a non-rotation. IC is ~0.066 for both — the *shape* of `σ` matters,
not its existence.

## "How do I tell a Vigenere from a substitution?"

The **IC**: `vigenere` ~0.038 (the `L`-alphabet mix flattens toward uniform),
`subst` ~0.066 (a `σ` preserves the multiset). Kasiski gives `L` for a
Vigenere; a `subst` has no `L`.

## "The IC is 0.05 — is it mono or poly?"

On a short `ct` the IC is noisy — the `flag{`/`CTF{` positions and common
letters carry the solve. Don't trust a 15-char IC; a real 0.05 reading on a
long `ct` is a transposition (English counts, scrambled order).

## "The anneal gave `gLAG{...}`"

A partially-right `σ` — the `flag{` positions reveal which `σ` entries are
wrong. `σ⁻¹(g)` should be `f` — swap `σ(g)↔σ(f)` and re-score. Don't submit
`gLAG{...}` — it's a *candidate*, not a flag.

## "It's base64-looking — is it a cipher?"

`+/=`/hex/`01` → `enc_detect` — an *encoding*, no key. The charset is the
discriminator — always the first read.

## "A name is given — 'we used playfair'"

`other-ciphers.md`/`playfair-polybius.md` — `classical_solve` doesn't cover
it — a script / dcode.fr. `cipher_id` still reads the family (digraph shape).

## "The decode produced another ciphertext"

A layered cipher — `cipher_id` on the *output*, not a re-attack on the first
layer. `base64 → caesar → morse` — three independent decodes.

## "Is it verified?"

`enc(pt) == ct` and `pt` language — the re-encrypt is the verify; a plausible
read without it isn't confirmed.
