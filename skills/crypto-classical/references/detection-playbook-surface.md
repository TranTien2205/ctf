# Detection playbook surface — the reads → the family, the surface edition

## The charset → the tool

| Charset | The tool |
|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `enc_detect` |
| `ADFGVX`/`AB`×5 | `other-ciphers`/`playfair-polybius*` |
| letters-only | `cipher_id` |
| letters+digits | `cipher_id` (partial) |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `cipher_id` (the crib) |

## The IC → the family

| IC | The family |
|---|---|
| ~0.066 | monoalpha — `caesar`/`subst`/`atbash` |
| ~0.038 | polyalpha — `vigenere` |
| ~0.05-0.066 | transposition — `railfence`/columnar |

## The chi² → the `k`/`σ`/reflection

| chi² | The family |
|---|---|
| one min `k` | `caesar` |
| flat | `subst` |
| reversed | `atbash` |

## Kasiski → the `L`

| `L` | The command |
|---|---|
| a period | `vigenere --keylen L` |
| no period | `subst`/`π`/autokey |

## The freq → the `σ`/reflection/`π`

| Freq | The family |
|---|---|
| ETAOIN-shaped | `subst` |
| reversed ETAOIN | `atbash` |
| flat | `vigenere` |
| English counts, scrambled | `π` |

## The verify

`pt` language + `enc(pt)=ct`.
