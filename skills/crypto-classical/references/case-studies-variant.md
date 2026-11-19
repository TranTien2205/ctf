# Case studies variant — the solve shapes, by family

## The `caesar` shapes

- **the bare blob** — `cipher_id` → chi² min `k` → `caesar --text`.
- **the `k` given** — "k=3" → `caesar --text`, read the `k=3` row.
- **the ROT13 flag** — `synt{...}` → `codecs.decode('rot13')`.
- **the keyed alphabet** — `subst` on the `k`-shifted output.

## The `atbash` shapes

- **the reversed blob** — `cipher_id` → reversed ETAOIN → `atbash --text`.
- **the `uozt{` flag** — `flag{` reversed → `atbash --text`.

## The `subst` shapes

- **the monoalphabetic** — `cipher_id` → IC~0.066, flat chi² → `subst`.
- **the keyword** — `σ = KEYWORD...` — the `σ` order reveals it.
- **the near-decode** — `gLAG{` → the `flag{` positions pin `σ`.
- **the affine** — `a·p+b` — brute the 312.

## The `vigenere` shapes

- **the keyed** — `cipher_id` → IC~0.038, Kasiski `L` → `vigenere --keylen`.
- **the keyword** — "the key is a word" → `vigenere --key <word>`.
- **the Beaufort** — `c=k-p` → `p=k-c`.
- **the autokey** — `key=primer+pt` → `p_i=c_i-p_{i-1}`.
- **the keyed-alphabet** — `vigenere` `L` cosets → `subst` per-coset.

## The `railfence` shapes

- **the zigzag** — `cipher_id` → scrambled letters → `railfence --text`.
- **the columnar** — `n=r·c` → brute `w`.
- **the route/scytale** — a grid path / a `w`-wrap.
- **the `π(σ(p))`** — un-scramble `π` → `subst`.

## The verify

`pt` language + `enc(pt)=ct`.
