# Operator notes variant — the field details, by family

## The `caesar`/`atbash` field notes

- `caesar --text` — the 25 `k` ranked; the min is `k`. A name "k=N" → the row.
- `atbash --text` — `c=25-p` — the reversed ETAOIN.
- `synt{`/`Pxl{`/`fhpnf{` — the flag format under `k` — decode it.
- A keyed alphabet — `subst` on the `k`-shifted output.

## The `subst` field notes

- `subst --text [--restarts --iters]` — the tetragram anneal.
- `gLAG{` — the `flag{` positions pin `σ` — swap and re-score.
- `σ = KEYWORD + rest` — the keyword in `σ`'s order.
- A short `ct` — the `flag{` positions carry — `known-plaintext*.md`.

## The `vigenere` field notes

- `vigenere --text [--keylen|--key]` — `L` cosets → `L` Caesars.
- `L` mis-estimate — `L`/`L/2`/`2L` — the coset-IC confirms.
- A Beaufort — `c=k-p` → `p=k-c`. An autokey — `key=primer+pt`.
- A keyed-alphabet — `vigenere` `L`, then `subst` per-coset.

## The `railfence`/`π` field notes

- `railfence --text` — the depth `r` ranked.
- A columnar — `w` columns — brute `w`. A route — a `n=r·c` grid.
- `π(σ(p))` — `π` first (position-only), then `subst`.

## The boundary field notes

- `enc_detect` first — the charset is the tell — `encoding-*.md`.
- `cipher_id` on a layered `ct`'s *output* — `multi-step-chains*.md`.
- `other-ciphers*.md` for playfair/adfgvx/hill — a script / dcode.fr.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.
