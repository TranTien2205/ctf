# Corpus status — the honest wrap

## What was built

- ~255 reference modules + `../SKILL.md` + `../field-notes.md`.
- Three families, nine attack cards, the deep references, the discipline
  files, the index/map layers, the wrap files.

## The honest status

- **Catalogue** — no `crypto-ecc-dlog` chain in `knowledge/chains/` yet.
- Every command is the standard published mechanism, anchored to the real
  `crypto_attack.py` ids and `tools/crypto/*.py` modules.
- The proof is `x·G == Q`/`pow(g,x,p) == h`; the flag is `flag{`/`CTF{`
  in decoded bytes.

## The two invariants

- `--order` is `n`/`ord(G)`, never `p`.
- `--sigs` is a JSON **file**, never inline JSON.

## The handoff

Solve → `classify_solve` → `knowledge/chains/` card → `../field-notes.md`
`confirmed`. Fail → `knowledge/attempts/` falsifier + `reopen_if`.
