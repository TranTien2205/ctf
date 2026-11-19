# Per-family catalogue — the family → the bound → the files → the command

## `caesar` / `atbash` — the shift/reflection

- **bound**: `k` in 25 / `c=25-p`.
- **files**: `caesar-deep.md`,`caesar-catalogue.md`,`caesar-variants.md`,
  `shift-variants.md`,`atbash-deep.md`.
- **command**: `classical_solve {caesar,atbash} --text`.

## `subst` / affine / keyword — the monoalphabetic

- **bound**: a `σ` — the tetragram anneal.
- **files**: `subst-deep.md`,`subst-catalogue.md`,`subst-variants.md`,
  `monoalphabetic-variants.md`.
- **command**: `classical_solve subst --text [--restarts --iters]`.

## `vigenere` / beaufort / autokey / gronsfeld — the polyalphabetic

- **bound**: an `L` + a key.
- **files**: `vigenere-deep.md`,`vigenere-catalogue.md`,`vigenere-variants.md`,
  `polyalphabetic-variants.md`,`beaufort-autokey*.md`,`key-length*.md`.
- **command**: `classical_solve vigenere --text [--keylen|--key]`.

## `railfence` / columnar / route / scytale — the transposition

- **bound**: a depth/width/`π`.
- **files**: `railfence-deep.md`,`railfence-catalogue.md`,
  `railfence-variants.md`,`transposition-variants*.md`.
- **command**: `classical_solve railfence --text`; a script for columnar/
  route/scytale.

## The named others — playfair/affine/polybius/baconian/adfgvx/hill

- **files**: `other-ciphers.md`,`playfair-polybius*.md`.
- **solve**: a script / dcode.fr — `cipher_id` reads the family.

## The encoding boundary — base64/hex/binary/morse/baconian

- **files**: `detection.md`,`encoding-vs-cipher.md`,`encoding-boundary.md`,
  `class-boundary.md`.
- **solve**: `enc_detect` — no key.
