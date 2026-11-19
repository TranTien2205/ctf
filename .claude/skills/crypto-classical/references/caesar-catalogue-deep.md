# Caesar catalogue deep — the `k`-rotation family, fully indexed

## The family — `c = p + k mod 26`

One `k` for all letters — the 25 useful `k`; `k=0` identity. `cipher_id`'s
chi² finds it — the deep minimum is `k`.

## The variants — the `k`-rotation set

| Variant | The shift | The decode | The files |
|---|---|---|---|
| Caesar | `k` arbitrary | `p = c - k` | `caesar-deep.md`,`caesar-catalogue.md` |
| ROT13 | `k=13` | `codecs.decode('rot13')` — self-inverse | `caesar-*.md`,`shift-variants.md` |
| ROT5 | digits `k=5` | a `rot5` script | `shift-variants.md` |
| ROT18 | letters `k=13` + digits `k=5` | a `rot18` script | `shift-variants.md` |
| ROT47 | printable 33-126 `k=47` | `codecs`/`rot47` | `shift-variants.md` |
| Atbash | `c=25-p` reflection | `atbash --text` | `atbash-*.md` |
| keyed Caesar | `σ`-alphabet + `k` | `subst` on the output | `subst-*.md` |

## The detection — the chi² minimum

`chi²(k) = Σ (o_i - e_{i+k})² / e_{i+k}` — the `ct` shifted by `k` fit to
English `e`. One deep min → `caesar`. Flat → `subst` (non-cyclic `σ`).

## The solve — the `k` row

`classical_solve caesar --text` — the 25 `k` ranked; the min is `k`. A name
"k=N"/"rot"/"shifted" → the decoder directly.

## The polish — the `synt{` trap

`flag{` → `synt{`/`Pxl{`/`fhpnf{` under `k` — the flag *is* the encoded form.
Decode the format → `flag{...}`.

## The verify

`k` → `p = c - k` → language; `c = p + k` — the re-encrypt.

## The falsifier

No `k` produces language → `subst`/transposition.
