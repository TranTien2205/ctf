# Workflow catalogue — the procedures by scenario

## The bare-handout workflow

`detection*.md` → `cipher-identification.md` → `payload-dictionary*.md` →
`verify*.md` → `field-notes-index.md`. The default shape.

## The oracle workflow

`recon-order.md` (probe `sign(m)` twice for determinism) → collect sigs →
`r` dedupe → `hnp-ecdsa` or `ecdsa-nonce-reuse` → verify → record.

## The dlog workflow

`smoothness --n` → `pohlig-hellman` or `bsgs` → verify `g^x == h` → record.

## The defect-curve workflow

`Δ` check → `singular_ec` if `0`; `#E` count → `smart_attack` if `== p`;
`#E` smoothness → `pohlig-hellman` on the curve; else → `bsgs` or re-route.

## The invalid-curve workflow

`ec.py` for fake-curve construction → submit `P'` → `bsgs`/`pohlig` per
`d·P'` response → CRT → verify `d·G == Q`.

## The layered workflow

`multi-step-chains.md` — crypto step first (`d`/`x`), then the flag step
(forge/decrypt → `flag{…}`).

## The stuck workflow

`troubleshoot*.md` → `decide.py` → escalation rungs → `negative-results*.md`.
