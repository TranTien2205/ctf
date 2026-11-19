# Closing notes deep — the honest wrap, expanded

## What this corpus is

- A **detection-and-solve field manual** for `crypto-ecc-dlog`.
- Three families, nine attacks, one proof (`x·G == Q`/`g^x == h`), one
  record (`post-probe` verbatim), one escalation ladder (`decide.py`).

## What this corpus is not

- Not a flag cache — no verified `crypto-ecc-dlog` chains in
  `knowledge/chains/` yet. Every command is the standard published
  mechanism; nothing here is claimed as locally-verified experience.
- Not a full math text — `theory*.md` names the algorithm, not its
  textbook derivation.
- Not a substitute for the controller — `decide.py` chooses the next
  action; the corpus supplies the probes.

## The honest gaps

- **Pairing attacks** (MOV/Frey-Rück) — named, not tooled here.
- **Nonce lattices at scale** — pure-python `lll.py` bounds `m`.
- **Invalid-curve CRT depth** — the procedure is described; the per-curve
  oracles are challenge-specific.
- **`#E` counting at large `p`** — `smart`/`singular` assume `#E`
  countable or `p` small enough.

## The discipline it enforces

- Verify before believing (the scalar is not the key until `x·G == Q`).
- `--order` is `n`, `--sigs` is a file — the two highest-frequency traps.
- A falsifier that fires ends the attack; record the no in `attempts/`.
- A flag is `flag{` in decoded bytes — never the recovered scalar.

## The handoff

Solve → `classify_solve` → chain card → `../field-notes.md` `confirmed`.
Fail → `attempts/` falsifier + `reopen_if`. The next agent reads both.
