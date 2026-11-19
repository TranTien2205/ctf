# Per-condition — each family, the bound, the falsifier, the file

## `caesar` / `atbash`

- **bound**: a `k` in 25 / the reflection.
- **falsifier**: no `k` produces language → `subst`/transposition.
- **file**: `caesar-deep.md`, `caesar-catalogue.md`, `atbash-deep.md`.

## `subst` / affine / keyword

- **bound**: a `σ` — the anneal's tetragram score reaches language.
- **falsifier**: the anneal never reaches language → `π`/other.
- **file**: `subst-deep.md`, `subst-catalogue.md`.

## `vigenere` / beaufort / autokey / gronsfeld

- **bound**: an `L` + a key.
- **falsifier**: no `L` produces language → `subst`/`π`/other.
- **file**: `vigenere-deep.md`, `vigenere-catalogue.md`.

## `railfence` / columnar / route / scytale

- **bound**: a depth/width/`π`.
- **falsifier**: no depth/width produces language → a different `π` or not
  transposition.
- **file**: `railfence-deep.md`, `railfence-catalogue.md`.

## The named others

- **bound**: a script / dcode.fr — `other-ciphers.md`.
- **falsifier**: `cipher_id` doesn't match the family's shape.
- **file**: `other-ciphers.md`.

## The encoding boundary

- **bound**: `enc_detect` decodes it.
- **falsifier**: a letters-only `ct` → a cipher.
- **file**: `detection.md`, `class-boundary.md`.
