# Preconditions — what must hold before the solve

## The input

- A letter-only `ct` — letters transformed; `+/=`/hex/`01` → `enc_detect`.
- No key material — a `k`/`L`/`σ`/depth/*word* to recover.
- Enough length — under ~30 chars the statistics fail; the `flag{` positions
  carry.

## The tools

- `tools/cipher_id.py --text <CT>` — the identifier; `--selftest`.
- `tools/classical_solve.py {caesar,vigenere,subst,atbash,railfence} --text
  <CT>` — the solver; `--selftest`.
- `tools/enc_detect.py '<CT>` — the encoding path.
- A script / dcode.fr for the named others — `other-ciphers.md`.

## The context

- A `flag{`/`CTF{`/`SNT{` position if visible — the format leak.
- A cipher name in the text — `other-ciphers.md`.
- A "key"/"keyword"/"rail"/"fence"/"shift" hint → the family.

## The contract

`enc(pt) == ct` is the verify. `../field-notes.md` for real solves.
