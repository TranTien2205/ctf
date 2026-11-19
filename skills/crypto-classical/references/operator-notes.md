# Operator notes — the field-guide details

## The order

`cipher_id` → `cipher-identification` → `classical_solve <family>` →
`evidence` → `field-notes`.

## The tools

- `tools/cipher_id.py --text <CT>` / stdin / `--selftest` — the identifier.
- `tools/classical_solve.py {caesar,vigenere,subst,atbash,railfence} --text
  <CT> [--keylen] [--key] [--restarts] [--iters] [--selftest]` — the solver.
- `tools/enc_detect.py '<CT>` — the encoding path.
- A small script / dcode.fr / CyberChef for the named ciphers not in the tool.

## The signals

- IC ~0.066 → monoalpha; ~0.038 → polyalpha.
- chi² min `k` → `caesar`.
- Kasiski `L` → `vigenere --keylen`.
- scrambled letters → `railfence`/columnar.
- `+/=`/hex/`01` → encoding.

## The verify

`pt` language + `enc(pt)=ct`.

## The record

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`.
