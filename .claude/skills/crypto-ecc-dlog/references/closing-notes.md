# Closing notes — the session wrap

## What the class covers

Curve/nonce/dlog recovery — `d`, `x`, `k` are the deliverables. Three
families: nonce (reuse/bias/leak), dlog (PH/BSGS), defect (smart/singular/
invalid).

## The procedure to memorize

1. `r` dedupe → `ecdsa-nonce-reuse`.
2. `smoothness --n ord` → `pohlig-hellman`/`bsgs`.
3. `Δ`/`#E` → `singular_ec`/`smart_attack`.
4. `k` bound → `hnp-ecdsa`/`hnp`.
5. oracle validation → invalid curve.

## The non-negotiables

- `--order` is `n`, not `p`.
- `--sigs` is a file, not inline JSON.
- `required_signatures` before the lattice.
- `x·G == Q`/`g^x == h` before any claim.
- `post-probe` with verbatim output, falsifier on fail.

## The honest status

Catalogue — record the first real solve into `../field-notes.md` and file a
chain card via `classify_solve.py`.

## Where the rest lives

`detection*.md` reads · `cipher-identification.md` discriminate ·
`payload-dictionary*.md` solve · `verify*.md` verify ·
`per-family-*.md` families · `per-attack-*.md` cards · `troubleshoot*.md`
fix · `falsifiers*.md` stop · `negative-results*.md` record ·
`workflow*.md` procedure · `case-studies*.md` narrated · `README.md` index.
