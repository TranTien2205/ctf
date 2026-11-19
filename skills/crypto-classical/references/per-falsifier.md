# Per-falsifier — each close, the signal, the re-route

## `caesar` closed

- **Signal**: no `k` in 25 produces language.
- **Re-route**: `subst` (a non-cyclic `σ`) or transposition.

## `atbash` closed

- **Signal**: the reflection produces garbage.
- **Re-route**: `subst` (a general `σ`).

## `subst` closed

- **Signal**: the anneal never reaches language.
- **Re-route**: `π` (transposition — the multiset is the `σ` invariant) or a
  non-substitution.

## `vigenere` closed

- **Signal**: no `L` produces language.
- **Re-route**: `subst`/`π`/other; or a Beaufort (`c=k-p`) if only the key
  shape was wrong.

## `railfence` closed

- **Signal**: no depth/width produces language.
- **Re-route**: a different `π` (columnar/route) or `subst` (a letter-`σ`).

## Transposition closed

- **Signal**: the letter multiset *isn't* English → a `σ` over the letters
  first — `π(σ(p))` layered.
- **Re-route**: `subst` on the un-scrambled `ct`.

## Encoding boundary

- **Signal**: `+/=`/hex/`01`/`.-` → `enc_detect` — *not* a cipher.
- **Re-route**: `cipher_id` first; the charset is the discriminator.
