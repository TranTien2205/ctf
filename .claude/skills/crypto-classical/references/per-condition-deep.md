# Per-condition deep — each family, the bound, the falsifier, the file, annotated

## `caesar` / `atbash` — the shift/reflection

- **bound**: a `k` in 25 / the reflection `c=25-p`.
- **falsifier**: no `k` produces language → `subst`/transposition.
- **files**: `caesar-deep.md`,`caesar-catalogue.md`,`caesar-variants.md`,
  `shift-variants.md`,`atbash-deep.md`.
- **command**: `classical_solve {caesar,atbash} --text`.

## `subst` / affine / keyword — the monoalphabetic

- **bound**: a `σ` — the tetragram anneal reaches language.
- **falsifier**: the anneal never reaches language → `π` (transposition) or a
  non-substitution.
- **files**: `subst-deep.md`,`subst-catalogue.md`,`subst-variants.md`,
  `monoalphabetic-variants.md`,`language-scoring*.md`.
- **command**: `classical_solve subst --text [--restarts --iters]`.

## `vigenere` / beaufort / autokey / gronsfeld — the polyalphabetic

- **bound**: an `L` + a key.
- **falsifier**: no `L` produces language → `subst`/`π`/other; a Beaufort if
  the key shape is `c=k-p`; an autokey if `key=primer+pt`.
- **files**: `vigenere-deep.md`,`vigenere-catalogue.md`,`vigenere-variants.md`,
  `polyalphabetic-variants.md`,`beaufort-autokey*.md`,`key-length*.md`.
- **command**: `classical_solve vigenere --text [--keylen|--key]`.

## `railfence` / columnar / route / scytale — the transposition

- **bound**: a depth/width/`π`.
- **falsifier**: no depth/width produces language → a different `π` or not a
  transposition — `subst` if the multiset is English.
- **files**: `railfence-deep.md`,`railfence-catalogue.md`,
  `railfence-variants.md`,`transposition-variants*.md`.
- **command**: `classical_solve railfence --text`; a script for columnar/
  route/scytale.

## The named others — playfair/polybius/baconian/adfgvx/hill

- **bound**: a script / dcode.fr.
- **falsifier**: `cipher_id` doesn't match the family's shape (digraphs/pairs).
- **files**: `other-ciphers.md`,`playfair-polybius*.md`.

## The encoding boundary

- **bound**: `enc_detect` decodes it — no key.
- **falsifier**: a letters-only `ct` → a cipher.
- **files**: `detection.md`,`encoding-vs-cipher.md`,`encoding-boundary.md`,
  `class-boundary.md`.
