# Encoding vs cipher — the boundary, annotated

## The distinction

- **Encoding** — a *fixed positional code* — base64, hex, binary, Morse,
  Baconian, Polybius — **no key** — `enc_detect` decodes it directly.
- **Cipher** — a *keyed transform* — `σ`/`k`/`L`/`π` — `cipher_id` + the
  statistics + `classical_solve`.

## The charset is the tell

| Charset | Type |
|---|---|
| `A-Za-z0-9+/=` | base64 |
| `0-9a-f` | hex |
| `01` (8-bit groups) | binary |
| `.-`/`/` | Morse |
| `AB`×5 | Baconian |
| letters-only | a cipher |

## The trap — a cipher `ct` that looks encoded

A `subst` `ct` is letters-only — `enc_detect` doesn't fire. A `base64` decode
that yields a `ct` — *the layer* is encoding → cipher.

## The nested

`base64(ct) → caesar → morse → flag` — `enc_detect`/`cipher_id` per layer;
the layers are independent.

## The verify

`enc(pt) == ct` — or the encoding's own decode — `flag{` present.
