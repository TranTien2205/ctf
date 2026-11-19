# Summary variant — crypto-classical, by family

## The class

A classical cipher — letter-only `ct`, no key — shift/subst/polyalpha/
transposition/encoding. `cipher_id` discriminates; `classical_solve` solves.

## The `caesar`/`atbash` family

- **bound**: `k` in 25 / `c=25-p`.
- **the solve**: `classical_solve {caesar,atbash} --text`.
- **the files**: `caesar-*.md`,`atbash-*.md`,`shift-variants*.md`.

## The `subst` family

- **bound**: a `σ` — the tetragram anneal.
- **the solve**: `classical_solve subst --text [--restarts]`.
- **the files**: `subst-*.md`,`monoalphabetic-variants*.md`,`language-scoring*.md`.

## The `vigenere` family

- **bound**: an `L` + a key.
- **the solve**: `classical_solve vigenere --text [--keylen|--key]`.
- **the files**: `vigenere-*.md`,`polyalphabetic-variants*.md`,
  `beaufort-autokey*.md`,`key-length*.md`.

## The `railfence`/`π` family

- **bound**: a depth/width/`π`.
- **the solve**: `classical_solve railfence --text`; a script for columnar/
  route/scytale.
- **the files**: `railfence-*.md`,`transposition-variants*.md`.

## The named others + the encoding boundary

- **the others**: `other-ciphers*.md`,`playfair-polybius*.md` — a script.
- **the encoding**: `enc_detect` — `encoding-*.md` — no key.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present — `verify*.md`.
