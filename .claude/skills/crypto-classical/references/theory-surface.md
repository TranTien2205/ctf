# Theory surface — the facts, one-glance

## The statistics — the one-line versions

- **IC** — `Σn_i(n_i-1)/N(N-1)` — ~0.066 mono/`π`, ~0.038 poly.
- **chi²** — `Σ(o-e)²/e` per `k` — the min is `k` (Caesar); flat is `σ`.
- **Kasiski** — `gcd` of repeated-n-gram gaps → `L`.
- **tetragram** — `Σ log p(quad)` — the `σ` anneal objective.
- **frequency** — ETAOIN — `σ`-preserved; `π` preserves the multiset.

## The facts — the lemmas

- **Caesar ⊂ substitution** — a shift is a `σ`.
- **`L` is the key length** — Kasiski/IC estimate; `L` Caesars find the key.
- **`flag{` leaks the transform** — the format pins `σ`/`k`/`key`/`π`.
- **A near-decode is a candidate** — `gLAG{` — polish.
- **A layered cipher** — `cipher_id` on each output.
- **The charset decides enc-vs-cipher** — `+/=`/hex/`01` → `enc_detect`.
- **`π(σ(p))` order matters** — `π` first, then `σ`.
- **`σ = KEYWORD + rest`** — the keyword shows in `σ`'s order.
- **autokey has no `L`** — `key=primer+pt` — the `L` estimator reads nothing.

## The verify

`pt` language + `enc(pt)=ct`.
