# Detection playbook deep — the ordered discriminate, annotated

## Step 0 — the charset

`+/=`/hex/`01`/`.-`/`/`/`ADFGVX` → `enc_detect`/`other-ciphers` — *stop*, an
encoding or a fractionation. Letters-only → a cipher — continue.

## Step 1 — `cipher_id`

`python3 tools/cipher_id.py --text 'CT'` — IC/chi²/Kasiski/freq/verdict.

## Step 2 — the IC split

- **~0.066** → monoalpha — go to chi².
- **~0.038** → polyalpha — `vigenere --keylen L` (Kasiski `L` or IC-coset).
- **~0.05-0.066** → transposition — `railfence`/columnar/route — the `n` grid.

## Step 3 — the monoalpha split

- **chi² one min at `k`** → `caesar --text`.
- **chi² flat** → `subst --text` — a non-cyclic `σ`.
- **reversed ETAOIN** → `atbash --text`.
- **digraph-structured** → `playfair` → `other-ciphers.md`.

## Step 4 — the transposition split

- **a depth `r`** → `railfence --text`.
- **a width `w`/key** → a columnar — brute `w`.
- **a `n=r·c` route** → a script — the path.

## Step 5 — the named other

A name in the text → `other-ciphers.md`/`playfair-polybius.md` → a script /
dcode.fr.

## Step 6 — the verify

`pt` language + `enc(pt)=ct` — the family is a lead until the decode.
