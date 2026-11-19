# Workflow deep 2 — the procedures, expanded

## Phase 0 — the reads

```bash
python3 tools/cipher_id.py --text 'CT'
```

- the charset — letters-only vs `+/=`/hex/`01`/`.-`/`ADFGVX` (`enc_detect`/
  `other-ciphers`)
- the IC — ~0.066 mono / ~0.038 poly / ~0.05 `π`
- the chi² — one min `k` (`caesar`) / flat (`subst`) / reversed (`atbash`)
- Kasiski — the `L` (`vigenere`)
- the frequency — ETAOIN (`σ`) / reversed (`atbash`) / flat / scrambled (`π`)
- a cipher name in the text — `other-ciphers.md`
- `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` positions — the crib
- the length — `n = r·c` → a grid

## Phase 1 — the discriminate

`cipher-identification.md`,`detection-matrix*.md`,`per-family-map.md` —
the (IC × chi² × Kasiski × charset) tuple → the family.

## Phase 2 — the solve

```bash
python3 tools/classical_solve.py <family> --text 'CT' [--keylen|--key|--restarts|--iters]
```

`payload-dictionary*.md` for the flag set; `other-ciphers.md` for the named
others; `enc_detect` for the encoding boundary.

## Phase 3 — the verify

`pt` language → `enc(pt) == ct` → `flag{`/`CTF{` present → the flag —
`verify*.md`,`evidence*.md`.

## Phase 4 — the record / escalate

`post-probe` · `classify_solve.py` · `../field-notes.md` · `decide.py` — the
6-rung escalate — `chain_match`,`reclassify`,`writeup_search`,`novel_plan`,
`fanout_sweep`,`solver_handoff`.

## The falsifier-first rule

The bound *before* the solve — no `k`/`L`/language → the family closes.
