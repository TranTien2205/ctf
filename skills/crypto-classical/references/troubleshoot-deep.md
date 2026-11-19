# Troubleshoot deep — the failure modes, annotated

## `cipher_id` gives the wrong family

**Why**: the IC is noisy on a short `ct`, or the `ct` is layered (the outer
layer's stats dominate), or a partial cipher (digits/spaces exempt).

**Fix**: trust the `flag{` positions and the charset over a marginal IC; on a
layered `ct`, `cipher_id` on the *output* of a decode.

## `classical_solve caesar` gives garbage

**Why**: the `σ` isn't a rotation — a general `subst`; or a keyed alphabet; or
digits/punct in `ct` confusing the shift.

**Fix**: `subst` on the `ct`; strip non-letters first; a `σ` over a keyed
alphabet is still a `σ`.

## `classical_solve vigenere` gives garbage

**Why**: `L` mis-estimated; or a Beaufort (`c=k-p`) not a Vigenere (`c=p+k`);
or an autokey (running `pt` key, not fixed `L`); or not a polyalpha at all.

**Fix**: try `L`, `L/2`, `2L`; the coset-IC confirms. A Beaufort → `c=k-p`.
An autokey → `key=primer+pt`. IC~0.066 → `subst`.

## `classical_solve subst` never reaches language

**Why**: not a `σ` — a `π` (transposition) or non-substitution; the `ct` too
short for the tetragram model; `--restarts`/`--iters` too low.

**Fix**: `railfence`/columnar if the letters are English; more `--restarts`;
the `flag{` positions anchor `σ` on a short `ct`.

## `classical_solve railfence` gives garbage

**Why**: a columnar (width `w`, not depth `r`); a route (spiral); a `σ`
(letter-bijection) not a `π`.

**Fix**: brute `w`; the grid `n = r·c`; `subst` if the multiset is English.

## The decode produces another `ct`

**Why**: a layered cipher.

**Fix**: `cipher_id` on the *output* — the layers are independent; decode each.

## The `flag{` reads `synt{`/`Pxl{`/`fhpnf{`

**Why**: the flag is itself encoded — ROT13/`k`-shifted.

**Fix**: decode the format — `synt{` → `flag{` under ROT13.
