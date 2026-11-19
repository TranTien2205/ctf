# Evidence — what proves a PRNG recovery

## The `class` evidence

A **predicted held-back output reproduced exactly** — verbatim:

```
predicted 0x9f3a21bc  observed 0x9f3a21bc
```

Not "the outputs look right", not a statistical argument — a bit-for-bit
reproduction of a value held back from the recovery.

## The `impact` evidence

The flag/token the recovered generator produces:

- the predicted next token/session-id/nonce that authenticates you,
- `flag{...}`/`CTF{...}` from the recovered stream or the forged object.

## The two-kinds boundary

- **class** — `predict == held-back` (the recovery is real).
- **impact** — the flag (the recovery did something).

## The `post-probe` shape

```
--hypothesis-id <attack-id>
--class crypto-prng
--evidence-kind class|impact
--evidence '<verbatim predicted==observed line>'
--response '<the bytes the evidence came from>'
```

`--evidence` must be a substring of `--response` — paste the tool output.

## The non-evidence

- A plausible-looking recovered `a`,`c`,`m` whose predictions miss.
- A statistical test (chi-square) — uniformity is not predictability.
- A single matching output by luck — reproduce a sequence.
- The flag-shaped string in the challenge description.

## The record

`post-probe` → `../field-notes.md` → `classify_solve`/`attempts`.
