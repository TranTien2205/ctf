# Detection matrix deep — the full IC × chi² × Kasiski × charset table

| IC | chi² | Kasiski | freq | charset | → family |
|---|---|---|---|---|---|
| ~0.066 | one min `k` | — | ETAOIN+k | letters | `caesar` |
| ~0.066 | flat | — | ETAOIN-shape | letters | `subst` |
| ~0.066 | reversed | — | Z,V,G top | letters | `atbash` |
| ~0.038 | — | `L` | flat | letters | `vigenere --keylen` |
| ~0.05-0.066 | — | — | English counts | letters | `railfence`/columnar |
| ~0.05-0.066 | — | — | English counts | letters | `route`/scytale |
| ~0.066 | — | — | digraph shape | letters | `playfair` |
| — | — | — | pairs | digits/letters | `polybius`/adfgvx |
| — | — | — | — | `+/=`/hex/`01` | `enc_detect` |
| ~0.066 | — | — | ETAOIN | letters+digits | partial cipher |
| low | — | — | — | digits+letters | a partial cipher |
| ~0.066 | — | — | ETAOIN | letters | `affine` (a `σ`) |

## The monoalpha split — IC~0.066

- **chi² one min `k`** → `caesar` — `k` is the min.
- **chi² flat** → `subst` — a non-cyclic `σ`.
- **reversed ETAOIN** → `atbash` — `σ` the reflection.
- **`σ` linear** (`a·p+b`) → `affine` — brute the 312.
- **digraph-structured** → `playfair` — the keyed square.

## The polyalpha split — IC~0.038

- **Kasiski `L`** → `vigenere --keylen L`.
- **no `L`** → `subst`/`π`/other, or `autokey` (no period).

## The `π` split — IC~0.05-0.066, scrambled

- **`n` composite** → `railfence`/`columnar`/`route`.
- **`n` a ribbon `w`** → `scytale`.

## The encoding split — the charset

- **`+/=`/hex/`01`/`.-`/`AB`/`ADFGVX`** → `enc_detect`/script — an encoding,
  not a `σ`.

## The verify

`pt` language + `enc(pt)=ct` — the table is a lead until the decode.
