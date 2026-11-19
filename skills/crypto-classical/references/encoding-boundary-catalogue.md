# Encoding boundary catalogue — the enc-vs-cipher split, indexed

## The distinction

- **Encoding** — a *fixed positional code*, no key — `enc_detect`.
- **Cipher** — a *keyed transform* — `cipher_id` + `classical_solve`.

## The charset table → the tool

| Charset | Type | The tool | The files |
|---|---|---|---|
| `A-Za-z0-9+/=` | base64 | `enc_detect` | `encoding-*.md` |
| `0-9a-f` | hex | `enc_detect` | `encoding-*.md` |
| `01` (8-bit) | binary | `enc_detect` | `encoding-*.md` |
| `.-`/`/` | Morse | `enc_detect` | `encoding-*.md` |
| `AB`×5 | Baconian | `enc_detect`/script | `playfair-polybius*.md` |
| `ADFGVX` | ADFGVX | `other-ciphers` → script | `other-ciphers*.md`,`playfair-polybius*.md` |
| digits `11`-`55` pairs | Polybius | `other-ciphers` → script | `playfair-polybius*.md` |
| letters-only | a cipher | `cipher_id` → `classical_solve` | `cipher-identification.md` |
| letters+digits | a partial cipher | `cipher_id` → `classical_solve` | `edge-cases*.md` |

## The trap — a cipher `ct` that looks encoded

A `subst` `ct` is letters-only — `enc_detect` doesn't fire; `cipher_id` reads
the `σ`. A `base64` decode that yields a `ct` — *the layer* is encoding →
cipher — `multi-step-chains*.md`.

## The nested

`base64 → caesar → morse → flag` — `enc_detect`/`cipher_id` per layer —
`multi-step-chains*.md`.

## The verify

`enc(pt) == ct` — or the encoding's own decode — `flag{` present.
