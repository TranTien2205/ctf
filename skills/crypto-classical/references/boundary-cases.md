# Boundary cases — the edge forms

## The `e`-analog boundaries

- `e`=1 → `c=m` — no, that's RSA. Here: `k=0` → `c=p`.
- `L`=1 → Vigenere = Caesar.
- `k=13` → ROT13 (self-inverse); `k=0` → `c=p`.
- `a=1,b=0` → Affine = identity.

## The length boundaries

- `n` short (<30 chars) — the statistics unreliable; the format positions carry.
- `n` composite → a grid; `n` square → a route.
- `n` = `L` → a single-period Vigenere = Caesar.

## The charset boundaries

- letters+digits → a partial cipher; digits may be kept.
- spaces kept → a transposition/partial monoalphabetic.
- `flag{`/`CTF{` visible → the format leaks.

## The degenerate

- `c=p` (no transform) — `cipher_id` says "not a cipher" or a `k=0` Caesar.
- A plaintext already language — the `ct` is the answer.
- A monoalphabetic with `σ`=identity → `c=p`.

## The verify

`pt` language + `enc(pt)=ct`.
