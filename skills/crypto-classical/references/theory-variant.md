# Theory variant — the facts, by family

## The `caesar`/`atbash` theory

- `c = p + k` — a cyclic rotation — chi² finds `k` (one min).
- `c = 25 - p` — a reflection — the reversed ETAOIN.
- IC ~0.066 — the multiset preserved cyclically.

## The `subst` theory

- `c = σ(p)` — a bijection — IC ~0.066, chi² flat, ETAOIN-shaped.
- the anneal — tetragram `Σ log p(quad)` — swap `σ` entries.
- `σ = KEYWORD + rest` — the keyword in `σ`'s order.
- `σ(p) = a·p+b` — Affine — 312 keys.

## The `vigenere` theory

- `c_i = p_i + k_{i mod L}` — `L` cosets — IC ~0.038, Kasiski `L`.
- `L` Caesars recover the key — each coset a Caesar.
- Beaufort `c=k-p`, autokey `key=primer+pt`, Gronsfeld digit-key.
- no `L` → autokey/running-key — a crib carries it.

## The `railfence`/`π` theory

- `c = π(p)` — a position-permutation — IC ~0.05-0.066.
- the multiset is *identical* — English counts, scrambled order.
- `n = r·c` → a grid — the `π` shape names the variant.

## The encoding theory

- `c = enc(p)` — a fixed code — no key — `enc_detect`.
- the charset is the tell — `+/=`/hex/`01`/`.-`/`ADFGVX`/`AB`×5.

## The verify

`pt` language + `enc(pt)=ct`.
