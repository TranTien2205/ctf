# Troubleshoot variant — the failure → the fix, by family

## `cipher_id` reads the wrong family

- **A short `ct`** — the IC is noisy → the `flag{` positions carry.
- **A layered `ct`** — the outer layer's stats dominate → `cipher_id` on the
  *output* of a decode.
- **A partial cipher** — digits/spaces exempt → strip them first.

## `caesar` gives garbage

- **Not a `k` shift** → `subst` (non-cyclic `σ`) or `π`.
- **A keyed alphabet** → `subst` on the `k`-shifted output.
- **Digits/punct in `ct`** → strip, decode, re-attach.

## `atbash` gives garbage

- **Not a reflection** → `subst` (a general `σ`).

## `vigenere` gives garbage

- **The `L` wrong** → try `L`, `L/2`, `2L`; the coset-IC confirms.
- **A Beaufort** → `c=k-p` → `p=k-c`.
- **An autokey** → `key=primer+pt` → `p_i=c_i-p_{i-1}`.
- **Not a polyalpha** → `subst`/`π`.

## `subst` never reaches language

- **Not a `σ`** → `π` (the multiset is the `σ` invariant) or a
  non-substitution.
- **The `ct` too short** → the `flag{` positions anchor `σ`.
- **`--restarts`/`--iters` up** → a harder `σ`.

## `railfence` gives garbage

- **A columnar** → brute `w`, not `r`.
- **A route/scytale** → a `w`-width wrap or a spiral.
- **Not a `π`** → `subst` (a letter-`σ`).

## The decode → another `ct`

- **A layered cipher** → `cipher_id` on the output.
