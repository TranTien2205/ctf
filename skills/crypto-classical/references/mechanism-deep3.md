# Mechanism deep 3 — the four transforms, the fifth boundary

## The shift — `c = p + k mod 26`

A cyclic rotation of the alphabet — `k` is the key. `cipher_id`'s chi² finds
it — the `k` that un-rotates `E`'s image back onto `E`. Atbash (`c=25-p`) is
a *reflection* — a `σ` too — the reversed-ETAOIN shape.

## The substitution — `c = σ(p)`

A bijection — the multiset structure preserved; `σ(E)` the top `ct` letter.
IC ~0.066; chi² flat. The anneal climbs tetragrams — `σ` swaps until the
`pt` is language. `σ = KEYWORD + rest` — a keyed alphabet — `σ` still solves
it; the keyword shows in the order.

## The polyalphabetic — `c_i = p_i + k_{i mod L}`

`L` cosets each a Caesar — the `L`-mix flattens the letters → IC ~0.038.
Kasiski: a repeated n-gram at gap `g` → `g` a multiple of `L`. `L` Caesars
recover the key — `LXFOPVEFRNHR` at `L=5` → `LEMON`. Beaufort `c=k-p`,
autokey `key=primer+pt`, Gronsfeld digit-key — the `L`-coset family.

## The transposition — `c = π(p)`

A permutation of *positions* — the multiset exactly preserved; IC ~0.05-0.066,
English counts, scrambled order. `π`'s shape names the variant: rail-fence
(zigzag `r`), columnar (key-ordered `w`), route (a grid path), scytale (a
`w`-wrap), block-perm (a `b`-key).

## The encoding — `c = enc(p)`, no key

A structured alphabet — base64 (64-char), hex (16), binary (8×2), Morse
(`.-`), Baconian (`AB`×5), Polybius (pairs), ADFGVX — a *bijection of a
different kind*: positional code, not a `σ` on 26. `enc_detect` decodes it;
the charset is the tell.

## The verify

`pt` language + `enc(pt) = ct` — the transform proven, the flag present.
