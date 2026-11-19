# Edge cases — the boundary forms

## The degenerate transforms

- `k=0` → `c=p` — `cipher_id` says "not a cipher"; the `ct` is the answer.
- `L=1` → Vigenere = Caesar.
- `k=13` → ROT13 (self-inverse).
- `a=1,b=0` → Affine = identity.
- `σ=identity` → `c=p`.

## The length edges

- `n` < ~30 → the statistics unreliable; the `flag{` positions carry.
- `n` = `L` → a single-period Vigenere = Caesar.
- `n` composite → a grid (`railfence`/columnar/route).
- `n` square → a route/spiral.
- `n` prime → no grid — a `σ`/`k`/`π` on positions only.

## The charset edges

- letters+digits → a partial cipher (letters transformed, digits kept).
- spaces kept → a transposition/partial monoalphabetic.
- `flag{`/`CTF{`/`SNT{`/`synt{` visible → the format leak.
- mixed case → the case is often a channel (Baconian binary).

## The layered edges

- `base64 → caesar → morse → flag` — `cipher_id` on each output.
- `π(σ(p))` — a transposition *of a substituted* text: un-scramble the `π`
  first (the multiset is position-preserved), then `subst`.

## The verify

`pt` language + `enc(pt)=ct`.
