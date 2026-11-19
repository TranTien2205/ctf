# Detection playbook — the ordered discriminate

## Step 0 — the charset

`+/=`/hex/`01`/`.-`/`/` → `enc_detect` — *stop*, an encoding.

## Step 1 — `cipher_id`

`python3 tools/cipher_id.py --text 'CT'` — IC/chi²/Kasiski/freq/verdict.

## Step 2 — the IC split

- **~0.066** → monoalpha — go to chi².
- **~0.038** → polyalpha — `vigenere --keylen L`.
- **~0.05-0.066** → transposition — `railfence`/columnar.

## Step 3 — the monoalpha split

- **chi² one min at `k`** → `caesar --text` (or `--k` — it's the 25).
- **chi² flat** → `subst --text` — a non-cyclic `σ`.
- **reversed ETAOIN** → `atbash --text`.

## Step 4 — the transposition split

- **a depth** → `railfence --text` — the depths ranked.
- **a width/key** → a columnar — brute `w`.

## Step 5 — the named other

A name in the text → `other-ciphers.md` → a script / dcode.fr.

## Step 6 — the verify

`pt` language + `enc(pt)=ct` — the family is a lead until the decode.
