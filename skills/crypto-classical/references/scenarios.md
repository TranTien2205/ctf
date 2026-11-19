# Scenarios — the challenge presentations

## The single ciphertext

A blob, no name → `cipher_id` → the family → `classical_solve <family>`.

## The named cipher

A name in the text → `classical_solve <family> --key` or `--text` — the
decoder directly.

## The keyed-but-unnamed

A "key" mentioned, no cipher name → `cipher_id` → likely `vigenere`/`subst` —
the key word tried first.

## The layered blob

`cipher_id` says "encoding" → decode → `cipher_id` again → the next layer.

## The wrong-charset

`+/=`/hex/`01` → `enc_detect.py` — an encoding, the flag inside.

## The short blob

A 20-char `ct` → the format positions + common letters carry the solve — the
statistics are unreliable.

## The verify

`pt` language + `enc(pt)=ct`.
