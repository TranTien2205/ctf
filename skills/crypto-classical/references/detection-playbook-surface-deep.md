# Detection playbook surface deep — the discriminate, the surface edition, expanded

## Step 0 — the charset

`+/=`/hex/`01`/`.-`/`ADFGVX`/`AB`×5 → `enc_detect`/`other-ciphers` — *stop*,
an encoding or a fractionation. Letters-only → `cipher_id`.

## Step 1 — `cipher_id --text`

IC/chi²/Kasiski/freq/verdict.

## Step 2 — the IC split

- **~0.066** → monoalpha — chi² splits it (`k`/`σ`/reflection).
- **~0.038** → polyalpha — `vigenere --keylen L`.
- **~0.05-0.066** → `π` — the `n = r·c` grid.

## Step 3 — the monoalpha split

- **chi² `k`** → `caesar`.
- **flat** → `subst`.
- **reversed** → `atbash`.
- **digraphs** → `playfair`.

## Step 4 — the `π` split

- **`n = r·c`** → `railfence`(depth)/columnar(width)/route(path).
- **`n` a ribbon `w`** → `scytale`.

## Step 5 — the named other

A name → `other-ciphers*.md`/`playfair-polybius*.md` → a script.

## Step 6 — the verify

`pt` language + `enc(pt)=ct`.
