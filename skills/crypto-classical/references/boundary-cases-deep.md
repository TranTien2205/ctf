# Boundary cases deep — the edge forms, annotated

## The `k=0` boundary

`c=p` — no transform. `cipher_id` reports "not a cipher" or a `k=0` chi² min.
The `ct` *is* the answer — don't "solve" it.

## The `L=1` boundary

Vigenere at `L=1` is a Caesar — `caesar` solves it; `vigenere --keylen 1`
confirms.

## The `L=n` boundary

`L = len(ct)` — each letter its own coset → a single-period Vigenere = a
Caesar on the coset means nothing — an `L=n` `key` is just a `σ`. Kasiski
reads `L=n` spuriously on a short `ct`.

## The `n` composite boundary

`n = r·c` — a grid → `railfence`(depth `r`)/columnar(width `w`)/route — try
the divisors.

## The `n` prime boundary

No grid — a `σ`/`k`/`π` on positions only.

## The `σ=identity` boundary

`c=p` — `cipher_id` "not a cipher" — the `ct` is the answer.

## The `σ` a two-letter swap boundary

`σ` = `A↔B` — the anneal finds it; the `flag{` positions find it faster.

## The charset edges

- letters+digits → a partial cipher — letters `σ`'d, digits kept.
- spaces kept → a transposition or a space-exempt `σ`.
- mixed case → a Baconian A/B channel — the case is the data.
- `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` → the format leak.

## The verify

`pt` language + `enc(pt)=ct`.
