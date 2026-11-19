# Per-falsifier deep — each close, the signal, the re-route, annotated

## `caesar` closed — no `k` produces language

- **Signal**: the 25 `k` rows are all non-language.
- **Re-route**: `subst` (a non-cyclic `σ`) or transposition (`π` — the multiset
  is the tell). A `σ` over a keyed alphabet reads near-`k` but is flat chi².

## `atbash` closed — the reflection produces garbage

- **Signal**: `c=25-p` doesn't decode.
- **Re-route**: `subst` — a general `σ` (atbash is a special `σ`).

## `subst` closed — the anneal never reaches language

- **Signal**: the tetragram score plateaus below English.
- **Re-route**: `π` (transposition — the multiset is preserved but the order
  is scrambled) or a non-substitution. `π(σ(p))` if the letters aren't English.

## `vigenere` closed — no `L` produces language

- **Signal**: every `L` coset-decode is non-language.
- **Re-route**: `subst`/`π`/other; a Beaufort (`c=k-p`) if the key shape was
  `+k` not `-p`; an autokey (`key=primer+pt`) if Kasiski read no period.

## `railfence` closed — no depth/width produces language

- **Signal**: no `r`/`w`/`π` gives language.
- **Re-route**: a different `π` (columnar/route — a `n=r·c` grid, not a depth)
  or `subst` (a letter-`σ` — the multiset is the `π` invariant).

## Transposition closed — the multiset isn't English

- **Signal**: the `ct` letters aren't English-counted.
- **Re-route**: `π(σ(p))` layered — un-scramble `π` (position-only) first,
  then `subst`.

## Encoding boundary — `+/=`/hex/`01`/`.-`

- **Signal**: the charset is structured, not letter-only.
- **Re-route**: `enc_detect` — *not* a cipher; `other-ciphers` for `ADFGVX`.
