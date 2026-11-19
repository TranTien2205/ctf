# Detection variant 2 — the reads, by the read's shape

## The `cipher_id` read — the statistics

- IC ~0.066 → monoalpha; ~0.038 → polyalpha; ~0.05 → `π`.
- chi² — `k` (Caesar) / flat (`subst`) / reversed (`atbash`).
- Kasiski — the `L` (vigenere).
- freq — ETAOIN (`σ`) / reversed (`atbash`) / flat / scrambled (`π`).

## The `ct`-shape read — the observable

- `+/=`/hex/`01`/`.-`/`ADFGVX`/`AB`×5 → `enc_detect`/`other-ciphers`.
- `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` → the crib.
- `n = r·c` → a grid.
- digraphs/pairs → `playfair`/`polybius`.
- mixed case → a Baconian/binary channel.

## The context read — the text

- a cipher name → `other-ciphers*.md`.
- a "key"/"keyword"/"rail"/"fence"/"columns" hint → the family.
- a "the key is a word" → `vigenere`/`subst`.

## The route

`cipher-identification.md` → the family → `classical_solve` —
`workflow*.md`.
