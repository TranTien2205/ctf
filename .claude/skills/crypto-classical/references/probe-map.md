# Probe map — the read → the signal → the family → the file

| Read | Signal | Family | File |
|---|---|---|---|
| `cipher_id` | IC~0.066, chi² `k` | caesar | `caesar-*.md` |
| `cipher_id` | IC~0.066, flat | subst | `subst-*.md` |
| `cipher_id` | IC~0.038, `L` | vigenere | `vigenere-*.md` |
| scrambled | letters preserved | railfence | `railfence-*.md` |
| reversed | `c=25-p` | atbash | `atbash-*.md` |
| `+/=`/hex | an encoding | enc_detect | `detection.md` |
| a name | the decoder | the family | `other-ciphers.md` |

## The verify

`pt` language + `enc(pt)=ct`.
