# Encoding boundary — the enc-vs-cipher split, annotated

## The distinction

- **Encoding** — a *fixed positional code*, no key — base64, hex, binary,
  Morse, Baconian, Polybius — `enc_detect` decodes it directly.
- **Cipher** — a *keyed transform* — `σ`/`k`/`L`/`π` — `cipher_id` + the
  statistics + `classical_solve`.

## The charset is the tell

| Charset | Type | The tool |
|---|---|---|
| `A-Za-z0-9+/=` | base64 | `enc_detect` |
| `0-9a-f` | hex | `enc_detect` |
| `01` (8-bit) | binary | `enc_detect` |
| `.-`/`/` | Morse | `enc_detect` |
| `AB`×5 | Baconian | `enc_detect`/script |
| `ADFGVX` | ADFGX | `other-ciphers` → script |
| digits `11`-`55` pairs | Polybius | `other-ciphers` → script |
| letters-only | a cipher | `cipher_id` → `classical_solve` |
| letters+digits | a partial cipher | `cipher_id` → `classical_solve` |

## The trap — a cipher `ct` that looks encoded

A `subst` `ct` is letters-only — `enc_detect` doesn't fire; `cipher_id` reads
the `σ`. A `base64` decode that yields a `ct` — *the layer* is encoding →
cipher.

## The nested

`base64(ct) → caesar → morse → flag` — `enc_detect`/`cipher_id` per layer;
the layers are independent.

## The verify

`enc(pt) == ct` — or the encoding's own decode — `flag{` present.
