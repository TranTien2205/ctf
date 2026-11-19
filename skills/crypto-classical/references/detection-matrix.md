# Detection matrix — the cross-table, IC × chi² × Kasiski × charset

| IC | chi² | Kasiski | charset | The family |
|---|---|---|---|---|
| ~0.066 | one min `k` | — | letters | `caesar` |
| ~0.066 | flat | — | letters | `subst` |
| ~0.038 | — | `L` | letters | `vigenere` |
| ~0.05-0.066 | — | — | letters (scrambled) | `railfence`/columnar |
| ~0.066 | reversed alphabet | — | letters | `atbash` |
| — | — | — | `+/=`/hex/`01`/`.-` | `enc_detect` |
| low | — | — | digits+letters | a partial cipher |

## The verify

`pt` language + `enc(pt)=ct` — the family is a lead until the decode.
