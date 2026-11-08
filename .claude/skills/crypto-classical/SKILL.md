---
name: crypto-classical
description: >
  Action-oriented depth skill for Classical cipher. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: misc-encoding-carrier, crypto-symmetric-oracle.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [crypto, classical, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Classical cipher

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

frequency analysis before any key guess — monoalphabetic spikes vs flattened vigenere polygraphs separate the families in seconds

**Falsifier** — the observation that closes this class: no classical transform (shift, substitution, transposition, polyalphabetic key) produces language from the ciphertext on standard tooling
## Recognise

A ciphertext blob, no key material, and either a named cipher in the
description or none. Caesar, Vigenere, substitution, transposition, Atbash,
Playfair, rail-fence — the classical family is identified by statistics, not
guessed.

## Confirm safely

All work is offline text. The confirmation is language: the decode produces
readable text or the flag format, and you can state WHICH transform did it.

## Identification order

0. `tools/cipher_id.py --text 'CT'` runs the statistics for you: IC,
   Caesar chi-squared sweep, and Kasiski period estimate in one pass,
   each family labelled a candidate. It also tells you when the blob is
   an encoding, not a cipher (route to `tools/enc_detect.py`).
1. Frequency analysis first — a monoalphabetic cipher keeps the natural
   spike pattern (ETAOIN); Vigenere and transposition flatten or preserve
   letters differently.
2. Index of coincidence — ~0.066 says monoalphabetic (shift/substitution),
   ~0.038 says polyalphabetic (Vigenere). IC also estimates the key period.
3. Named in the challenge? Go straight to the decoder — `dcode.fr`, CyberChef,
   or a five-line script. Do not re-derive a named cipher by hand.
4. Nothing matches? Try transposition shapes (rail-fence depths, columnar)
   and check whether the "ciphertext" is actually an encoding
   (misc-encoding-carrier) — b64-looking or hex-looking text is not a cipher.

`references/cipher-identification.md` carries the decision table.

## Traps

- Caesar is a special case of substitution — try all 25 shifts before writing
  substitution code.
- Vigenere keys are usually a word from the challenge text — try the
  obvious ones before Kasiski.
- A substitution solve that produces near-English but wrong flag format is
  often the right cipher with a partially-wrong key — check the flag-shaped
  positions first.

## Operational probe

`tools/classical_solve.py` carries the mechanical half — every family
cipher_id can name:

```bash
python3 tools/classical_solve.py caesar --text 'CT'       # 25 shifts ranked
python3 tools/classical_solve.py vigenere --text 'CT'     # IC/Kasiski -> key
python3 tools/classical_solve.py subst --text 'CT'        # annealing + polish
python3 tools/classical_solve.py railfence --text 'CT'    # rail depths ranked
```

`caesar` runs inside `vigenere`/`subst` anyway — if IC is ~0.066 start
with `subst`, if ~0.038 start with `vigenere`, and if the "cipher" fails
to read as language under every family, route to `tools/enc_detect.py`
because it was an encoding, not a cipher.

## Routing

Shares signals with: `../misc-encoding-carrier/`, `../crypto-symmetric-oracle/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/crypto-classical/references/README.md`
- `skills/crypto-classical/references/cipher-identification.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
