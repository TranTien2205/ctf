# Subst catalogue deep — the `σ` family, fully indexed

## The family — `c = σ(p)`

A bijection on 26 letters — the multiset preserved; IC ~0.066, chi² flat,
ETAOIN-shaped freq.

## The variants — the `σ` set

| Variant | The `σ` | The solve | The files |
|---|---|---|---|
| simple subst | any `σ` | `subst --text` the anneal | `subst-deep.md`,`subst-catalogue.md` |
| keyword | `KEYWORD + rest` | `subst` — the keyword in `σ`'s order | `subst-*.md`,`monoalphabetic-variants.md` |
| Caesar | a cyclic shift | `caesar --text` — faster | `caesar-*.md` |
| Atbash | `σ(i)=25-i` | `atbash --text` | `atbash-*.md` |
| Affine | `σ(p)=(a·p+b) mod 26` | brute the 312 | `monoalphabetic-variants.md` |
| Baconian | a 5-bit A/B *encoding* | `enc_detect`/script | `playfair-polybius*.md` |
| Polybius | a 5×5 grid pairs | `other-ciphers` → a script | `playfair-polybius*.md` |

## The detection — the flat chi² + ETAOIN shape

`cipher_id` — IC~0.066, chi² flat (no `k` fits a non-rotation), the `ct`
frequency ranked ETAOIN-shaped — `σ(E)` top, `σ(T)` next.

## The solve — the anneal

`subst --text [--restarts --iters]` — tetragram `Σ log p(quad)` hill-climb.

## The polish — the `gLAG{` trap

A near-decode — `σ⁻¹(g)` should be `f` — the `flag{` positions reveal the
wrong `σ` entries — swap and re-score.

## The verify

`σ⁻¹(c)=p` language; `σ(p)=c`.

## The falsifier

The anneal never reaches language → `π`/other — `per-falsifier*.md`.
