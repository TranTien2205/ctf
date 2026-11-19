# Verified chains deep — the chain cards, honest status

## The status

**None** — `crypto-classical` is a **catalogue** class. No chain card in
`knowledge/chains/` proves a local solve. `../field-notes.md` (skill root) is
where a real solve lands.

## The standard shapes — catalogue, not verified-here

| Chain | The shape |
|---|---|
| `cipher_id → caesar → flag` | the `k` shift |
| `cipher_id → atbash → flag` | the reflection |
| `cipher_id → vigenere --keylen → key → flag` | the `L`-coset |
| `cipher_id → subst → σ → flag` | the monoalphabetic |
| `cipher_id → railfence → depth → flag` | the `π` |
| `cipher_id → "encoding" → enc_detect → flag` | the boundary |
| `enc → cipher → enc → flag` | the layered |
| `flag{ positions → σ → flag` | the crib |

## The record

After a solve: `classify_solve.py --chain <id>` writes the card; a confirm
promotes the class from catalogue. `../field-notes.md` the per-challenge log;
`knowledge/attempts/` for a dead end.

## The verify

`pt` language + `enc(pt)=ct` — the chain card's standard.
