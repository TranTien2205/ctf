# Workflow — the end-to-end procedure

## Phase 1 — read the handout

`detection*.md` — name the group (curve name, order, generator, field size),
inventory signatures `(r, s, z)` if present, note any service/oracle shape.

## Phase 2 — the cheap gates

1. Any duplicate `r` in signatures? → `ecdsa-nonce-reuse`.
2. `crypto_attack.py smoothness --n <order>` — smooth → `pohlig-hellman`.
3. Custom curve: `#E == p`? → `smart_attack`. `Δ == 0`? → `singular_ec`.
4. Nonce bounded/short/partial? → `hnp-ecdsa`.
5. `x` bounded / small group? → `bsgs`.
6. Server takes points without validation? → invalid curve.

## Phase 3 — solve

`payload-dictionary*.md` has the exact commands. Prepare `--sigs` JSON for
ECDSA (`[r,s,z]` triples), `--order` for everything.

## Phase 4 — verify

The recovered scalar `x` (or `d`) must satisfy `x·G == Q` or `g^x == h mod p`
— `verify*.md`. Only then does the flag count.

## Phase 5 — record

`../field-notes.md` (root) — the `ct`/params, the attack used, the recovered
scalar, the verify result. A fail → `knowledge/attempts/` falsifier.

## The branch order (cheapest first)

```
sigs present?
├─ dup r → ecdsa-nonce-reuse (closed form)
├─ biased k → hnp-ecdsa (lattice)
└─ else → dlog or defect
custom curve?
├─ #E == p → smart_attack
├─ Δ == 0 → singular_ec
├─ #E smooth → pohlig-hellman
└─ none → bsgs if bounded, else re-read
```
