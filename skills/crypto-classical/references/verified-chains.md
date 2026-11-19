# Verified chains — the chain cards, honest status

## The status

**None** — `crypto-classical` is a **catalogue** class. No chain card in
`knowledge/chains/` proves a local solve. `../field-notes.md` (skill root) is
where a real solve lands.

## The standard shapes (catalogue, not verified-here)

- `cipher_id → caesar → flag` — the shift.
- `cipher_id → vigenere --keylen → key → flag` — the polyalphabetic.
- `cipher_id → subst → σ → flag` — the monoalphabetic.
- `cipher_id → railfence → depth → flag` — the transposition.
- `cipher_id → "encoding" → enc_detect → flag` — the boundary.

## The record

After a solve: `classify_solve.py --chain <id>` writes the card; a confirm
promotes the class from catalogue.
