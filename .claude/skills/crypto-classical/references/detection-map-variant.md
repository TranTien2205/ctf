# Detection map variant — the read → the signal → the family, by shape

## The IC-family map

| Read | Signal | Family |
|---|---|---|
| IC ~0.066 | monoalpha | `caesar`/`subst`/`atbash` |
| IC ~0.038 | polyalpha | `vigenere` |
| IC ~0.05-0.066 | transposition | `railfence`/columnar |

## The chi²-family map

| Read | Signal | Family |
|---|---|---|
| one min `k` | a shift | `caesar` |
| flat | a `σ` | `subst` |
| reversed | a reflection | `atbash` |

## The Kasiski-family map

| Read | Signal | Family |
|---|---|---|
| an `L` | a period | `vigenere` |
| no `L` | no period | `subst`/`π`/autokey |

## The freq-family map

| Read | Signal | Family |
|---|---|---|
| ETAOIN-shaped | a `σ` | `subst` |
| reversed ETAOIN | a reflection | `atbash` |
| flat | a polyalpha | `vigenere` |
| English counts, scrambled | a `π` | `railfence`/columnar |

## The charset-family map

| Read | Signal | Family |
|---|---|---|
| `+/=`/hex/`01` | an encoding | `enc_detect` |
| `ADFGVX`/`AB`×5 | a fractionation | `other-ciphers` |
| `flag{`/`CTF{`/`SNT{`/`synt{` | a crib | `known-plaintext` |
| digraphs/pairs | a square/grid | `playfair`/`polybius` |
| letters-only | a cipher | `cipher_id` |

## The verify

`pt` language + `enc(pt)=ct`.
