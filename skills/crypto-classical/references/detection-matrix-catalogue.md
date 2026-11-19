# Detection matrix catalogue — the discriminator tables, indexed

## The full table — `detection-matrix*.md`

| IC | chi² | Kasiski | freq | charset | → family |
|---|---|---|---|---|---|
| ~0.066 | one min `k` | — | ETAOIN+k | letters | `caesar` |
| ~0.066 | flat | — | ETAOIN-shape | letters | `subst` |
| ~0.066 | reversed | — | Z,V,G top | letters | `atbash` |
| ~0.038 | — | `L` | flat | letters | `vigenere --keylen` |
| ~0.05-0.066 | — | — | English counts | letters | `railfence`/columnar |
| ~0.066 | — | — | digraph shape | letters | `playfair` |
| — | — | — | pairs | digits/letters | `polybius`/adfgvx |
| — | — | — | — | `+/=`/hex/`01` | `enc_detect` |
| ~0.066 | — | — | ETAOIN | letters+digits | partial cipher |

## The monoalpha split — IC~0.066

- chi² one min `k` → `caesar`; flat → `subst`; reversed → `atbash`;
  linear (`a·p+b`) → `affine`; digraphs → `playfair`.

## The polyalpha split — IC~0.038

- Kasiski `L` → `vigenere --keylen`; no `L` → `subst`/`π`/autokey.

## The `π` split — IC~0.05-0.066, scrambled

- `n` composite → `railfence`/`columnar`/`route`; a `w`-wrap → `scytale`.

## The encoding split — the charset

- `+/=`/hex/`01`/`.-`/`AB`/`ADFGVX` → `enc_detect`/script.

## The verify

`pt` language + `enc(pt)=ct` — the table is a lead until the decode.
