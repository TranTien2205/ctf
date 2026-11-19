# Checklist deep — the full audit before, during, after

## Before the attack

- [ ] The sheet is filled — `n`,`e`,`c` counts, the leak, the keygen tell.
- [ ] `crypto_attack.py list` ran — the inventory + bounds seen.
- [ ] The discriminator picked an id — the row written down.
- [ ] The bound checked — `per-bound.md` read, the bound within reach.
- [ ] `lll_backend` noted — `fpylll` absent → pure-python LLL, slower.

## During the attack

- [ ] `<id> --help` read — the real flag names, not guessed.
- [ ] The args are integers — `0x…` or decimal, not strings.
- [ ] The cheap attacks ran first — fermat, batch-gcd, small-e, common-mod,
      pollard, wiener before the lattice.
- [ ] A bound exceeded → recorded as a negative, not retried.
- [ ] The falsifier observed → the next discriminator row.

## After the attack — the recovery

- [ ] `pow(m,e,n)==c` for a plaintext — run, not assumed.
- [ ] `p*q==n` for a factor — run.
- [ ] `pow(c,d,n)==m` + `pow(m,e,n)==c` for a `d`.
- [ ] A padded `m` — strip `\x00\x02<pad>\x00` / OAEP for the flag.
- [ ] `eth-root` — each `gcd` candidate tried, `pow`+format picks.

## The record

- [ ] `solved/<name>/` — the evidence tuple.
- [ ] `classify_solve.py --chain <id>` — after a solve.
- [ ] `knowledge/attempts/` — for a dead end, each bound.
- [ ] `../field-notes.md` — the confirmed/proposed entry.
- [ ] `hooks.py post-probe` — `--hypothesis-id`,`--class`,`--evidence-kind`,
      `--evidence`,`--response` for a `confirms`.

## The stop rules

- [ ] 5 probes in one family, no new signal → change the row.
- [ ] A bound exceeded → record, escalate.
- [ ] Every bound met → `class-boundary` — the bug isn't in the RSA.
- [ ] The flag verified → report, write the chain card.
