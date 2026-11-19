# Troubleshoot — the failure → the fix

## `cipher_id` gives the wrong family

- **IC near the 0.05 line** — a short `ct` or a partial cipher; the `flag{`
  positions carry.
- **The `ct` is layered** — `cipher_id` on the *output* of a decode.

## `classical_solve caesar` gives garbage

- **Not a `k` shift** — `subst` (a non-cyclic `σ`) or transposition.
- **A keyed alphabet** — `subst` on the output.
- **Digits/punct in `ct`** — strip them, decode, re-attach.

## `classical_solve vigenere` gives garbage

- **The `L` is wrong** — try `L`, `L/2`, `2L`; the coset-IC confirms.
- **A Beaufort** — the `c=k-p` reciprocal — try the reciprocal decode.
- **An autokey** — `key = primer + pt` — not a fixed `L`.
- **Not a polyalphabetic** — `subst`/transposition.

## `classical_solve subst` never reaches language

- **Not a `σ`** — `π` (transposition) or a non-substitution.
- **The `ct` is too short** — the anneal needs text; the `flag{` positions
  carry.
- **`--restarts`/`--iters` up** — a harder `σ`.

## `classical_solve railfence` gives garbage

- **A columnar** — brute `w`, not `r`.
- **A route/scytale** — a `w`-width wrap or a spiral.
- **Not a transposition** — `subst` (a letter-`σ`).

## The decode produces another `ct`

A layered cipher — `cipher_id` on the *output*; the next layer.
