# Cipher identification — the discriminator table

## The (IC, chi², Kasiski, charset) → family map

| IC | chi² | Kasiski | freq | → family |
|---|---|---|---|---|
| ~0.066 | one min `k` | — | ETAOIN shifted by `k` | `caesar` |
| ~0.066 | flat | — | ETAOIN-shaped | `subst` |
| ~0.066 | reversed | — | Z,V,G common | `atbash` |
| ~0.038 | — | `L` | flat | `vigenere --keylen L` |
| ~0.05-0.066 | — | — | English counts, scrambled | `railfence`/columnar |
| — | — | — | `+/=`/hex/`01`/`.-` | `enc_detect` |
| low | — | — | digits+letters | a partial cipher |

## The family → the solve

| Family | Command |
|---|---|
| `caesar` | `classical_solve caesar --text` |
| `atbash` | `classical_solve atbash --text` |
| `subst` | `classical_solve subst --text` |
| `vigenere` | `classical_solve vigenere --text --keylen L` |
| `railfence` | `classical_solve railfence --text` |
| encoding | `enc_detect` |
| named other | a script / `other-ciphers.md` |

## The short-ct rule

Under ~30 chars the statistics are unreliable — the `flag{`/`CTF{` positions
and common letters carry the solve. Anchor `σ`/`k`/`key` from the format.

## The layered rule

A decode that yields another `ct` — `cipher_id` on the *output*, not a
re-attack on the same layer.

## The verify

`pt` language + `enc(pt)=ct` — the family is a lead until the decode proves it.
