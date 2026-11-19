# Caesar variants — the `k`-rotation family, annotated

## The family

`c = p + k mod 26` — one `k` for all letters. The 25 useful `k`; `k=0` is
identity. `cipher_id` finds it by chi² — the minimum is `k`.

## The variants

### Caesar — `k` arbitrary

`classical_solve caesar --text` — the 25 `k` ranked by chi²; the min is `k`.

### ROT13 — `k=13`

Self-inverse — `codecs.decode(ct, 'rot13')`. `flag{` → `synt{`. A flag that
reads `synt{...}` is the ROT13 of the flag — decode it.

### ROT5 — digits `k=5`

`d → (d+5) mod 10` — only digits shifted. A `flag{...}` with digits ROT5'd.

### ROT18 — letters ROT13 + digits ROT5

The combined printable shift — letters `k=13`, digits `k=5`.

### ROT47 — printable ASCII 33-126 `k=47`

`!..~` rotated by 47 — `codecs`/a `rot47` decode. The charset is `!..~` not
`A-Z`.

### Atbash — `c = 25 - p`

A *reflection*, not a rotation — `atbash --text`; reversed ETAOIN shape.

### Keyed Caesar — `σ`-alphabet + `k`

`c = keyed[(keyed⁻¹(p) + k) mod 26]` — a shift over a `KEYWORD`-mixed
alphabet → the output is a `σ` — `subst` on the output.

## The detection — the chi²

`chi²(k) = Σ (o_i - e_{i+k})² / e_{i+k}` — the `ct` shifted by `k` fit against
English `e`. A Caesar has **one deep minimum** at `k` — the un-rotation. A
`subst` is flat — no `k` fits a non-rotation.

## The verify

`k` → `p = c - k` → language; `c = p + k` — the re-encrypt check.

## The falsifier

No `k` produces language → `subst` (a non-cyclic `σ`) or transposition.

## The traps

- **`k=13` on `pt`** — `flag{` reads `synt{` — decode it.
- **A keyed alphabet** — `subst` on the `k`-shifted output.
- **ROT5/18/47** — a `codecs`/`rot` script, not `caesar --text`.
