# Case studies deep 2 — more solve shapes

## The "k is given" case

A `ct` + "k=3" in the text → `caesar --text` and read the `k=3` row — no
statistics needed.

## The ROT13 flag

`ct` reads `synt{...}` — `flag{` under ROT13. `codecs.decode(ct,'rot13')` →
`flag{...}` — the flag is the *encoded* form.

## The short-blob case

A 15-char `ct` — the IC is unreliable. `flag{` at position 0 → `σ⁻¹(ct[0])=f`
etc. → the `σ` anchored by the format → `subst` polishes.

## The "key is a poem word" case

"the key is a word from the poem" → try the obvious words (`LEMON`,`SECRET`,
the title) before Kasiski — `vigenere --key <word>`.

## The Beaufort trap

A Vigenere-decode gives garbage → try `c=k-p` (Beaufort) — the reciprocal.

## The columnar case

Scrambled letters, `n=24=4·6` → brute `w` — fill `r×w`, read columns in key
order → `flag{...}`.

## The `π(σ(p))` layered case

IC~0.066 but the letters aren't English → un-scramble `π` (position-only) →
`subst` the un-scrambled `ct` → `flag{...}`.

## The verify

`pt` language + `enc(pt)=ct`.
