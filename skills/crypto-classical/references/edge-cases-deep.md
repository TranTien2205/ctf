# Edge cases deep — the boundary forms, annotated

## The degenerate transforms

- **`k=0`** — `c=p` — `cipher_id` reports "not a cipher" or a `k=0` min. The
  `ct` *is* the answer.
- **`L=1`** — Vigenere = Caesar — `caesar` solves it; `--keylen 1` confirms.
- **`k=13`** — ROT13 — self-inverse; `codecs.decode(ct,'rot13')`.
- **`a=1,b=0`** — Affine = identity.
- **`σ=identity`** — `c=p`.
- **`σ` a single swap** — a two-letter transposition `A↔B` — the anneal finds
  it but the `flag{` positions find it faster.

## The length edges

- **`n` < ~30** — the IC/chi²/Kasiski are unreliable; the `flag{`/`CTF{`
  positions + common letters carry the solve.
- **`n = L`** — a single-period Vigenere = Caesar.
- **`n` composite** — `n = r·c` → a grid — `railfence`/columnar/route.
- **`n` square** — a spiral/route — fill `√n×√n`.
- **`n` prime** — no grid — a `σ`/`k`/`π` on positions.

## The charset edges

- **letters+digits** — a partial cipher; digits kept, letters transformed.
- **spaces kept** — a transposition or a partial monoalphabetic (space isn't
  `σ`'d).
- **mixed case** — the case is often a *channel* — Baconian A/B, or upper/lower
  carrying a binary.
- **`flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{`** — the format leak — the
  format survives `σ`/`k`/`π`.

## The layered edges

- **`base64 → caesar → morse`** — `cipher_id` on each output.
- **`π(σ(p))`** — a transposition *of* a substituted text — the letters aren't
  English, but un-scrambling `π` (position-only) reveals the `σ`. Order: `π`
  first, then `σ`.
- **`σ(π(p))`** — rarer — the `σ` scrambles the letter values but `π` the
  positions; the solve order depends on which transform the `cipher_id` stats
  surface.

## The verify

`pt` language + `enc(pt)=ct` — each edge is still verified by re-encryption.
