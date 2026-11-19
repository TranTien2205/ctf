# Per-family map — the family → the bound → the file

## `caesar` / `atbash`

- **bound**: `k` in 25 / the reflection.
- **files**: `caesar-deep.md`,`caesar-catalogue.md`,`shift-variants.md`,
  `atbash-deep.md`.
- **command**: `classical_solve {caesar,atbash} --text`.

## `subst` / affine / keyword

- **bound**: a `σ` — the anneal.
- **files**: `subst-deep.md`,`subst-catalogue.md`,`monoalphabetic-variants.md`.
- **command**: `classical_solve subst --text [--restarts --iters]`.

## `vigenere` / beaufort / autokey / gronsfeld

- **bound**: an `L` + a key.
- **files**: `vigenere-deep.md`,`vigenere-catalogue.md`,
  `polyalphabetic-variants.md`,`beaufort-autokey.md`,`key-length.md`.
- **command**: `classical_solve vigenere --text [--keylen|--key]`.

## `railfence` / columnar / route / scytale

- **bound**: a depth/width/`π`.
- **files**: `railfence-deep.md`,`railfence-catalogue.md`,
  `transposition-variants.md`.
- **command**: `classical_solve railfence --text`; a script for columnar/route.

## The named others

- **files**: `other-ciphers.md`,`playfair-polybius.md`.
- **solve**: a script / dcode.fr.

## The encoding boundary

- **files**: `detection.md`,`encoding-vs-cipher.md`,`class-boundary.md`.
- **solve**: `enc_detect`.
