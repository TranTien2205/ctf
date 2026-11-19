# Field notes catalogue — the record shape, indexed

## The record components

| Component | Files |
|---|---|
| hypothesis-id | `evidence*.md` |
| class | `evidence*.md` |
| evidence kind (`class`/`impact`) | `evidence*.md` |
| verbatim evidence | `evidence*.md`,`verify*.md` |
| response (the bytes) | `evidence*.md` |
| the params | `field-notes-index.md` |
| the `--sigs`/`--order`/flags used | `payload-dictionary*.md` |
| the falsifier + reopener | `negative-results*.md` |

## The record files

`../field-notes.md` (skill root) — entries `proposed` → `confirmed`.
`field-notes-index.md` — the record-shape index.
`../../../LEARNING_LOOP.md` (root) — the loop that promotes solves.
`knowledge/chains/` — the card a solve produces.
`knowledge/attempts/` — the kill map a fail produces.

## The record commands

- `post-probe` — the ledger gate (evidence ⊆ response).
- `classify_solve.py` — files the chain card.
- `state.py --strategy-used <rung>` — records an escalation rung.

## The record checklist

`checklist*.md` → `operator-checklist.md` → `detection-checklist*.md`.
