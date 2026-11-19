# Common questions deep — the second-order questions

`common-questions.md` is the field FAQ. This module answers the
questions that come up mid-solve, when the simple answers ran out.

## "The allowlist falsified — why am I still probing nested fields?"

Because the falsifier fired at the TOP-LEVEL binder. `{...req.body}`
with a shallow allowlist — `pick(body, ['username','password'])` —
blocks `role` but says nothing about `{"user": {"role": "admin"}}`:
`user` may itself be allowlisted (it's a legit field — profile data
nests under it), and its sub-fields bind unsupervised. The nested
probe is a different code path, not a spelling variant. Depth matters:
falsifier at depth-1 leaves depth-2 open.

## "Serial replay 409'd — is replay dead?"

Serial replay at THIS endpoint is dead. The dedup has coverage
questions still open: key scope (`(user,code)` vs `(code)` vs
`requestId`), endpoint scope (`/redeem` blocked, `/claim` maybe not),
and the atomicity question — `check-then-set` non-atomically is the
parallel window, which is `web-race-condition`, not a dead end.

## "The transform gap confirmed — why doesn't my `id` reach the target?"

The arithmetic has more moving parts than the shape suggests:

- **`S` wrong**: derive the stride empirically — two accepted `id`
  values and their observed addresses give `S = (a2-a1)/(id2-id1)`.
- **`off` wrong**: the base offset may include a header/alignment term.
- **`w` wrong**: the wrap modulus is the word width — 16-bit index
  registers vs 32-bit addresses vs 64-bit pointers wrap at different
  heights.
- **`S` even**: the reachable set is a congruence class — your target
  `T` may be unreachable for ANY `id`; pick `T'` inside
  `{off + id*S mod 2^w}`.

## "I confirmed `role:admin` — where's the flag?"

The role is a state, not the sink. The flag is behind the ROLE-GATED
surface: enumerate what `role=admin` unlocks — the bundle's route
table (`bundle_miner` output — routes gated on `role` appear in the
JS), the source's `isAdmin` middleware uses, the `/admin*` paths.
The flag is typically a FIELD inside an admin view (`/admin/config`,
`/admin/flag`), not a top-level `/flag`.

## "Why does the skill say 'five probes then change layer'?"

Because the alphabet is a cover — each mechanism is a cell, and five
negatives inside a cell measure that the cell's layer is rejecting
uniformly. The Polynomial lesson: an agent left alone mutates spelling
indefinitely inside one cell. `decide.py` enforces the bound; the
falsifier usually closes the cell at probe 2, making the five a
ceiling, not a target.

## "What's the difference between a falsifier and a negative result?"

Falsifier: the mechanism is provably absent HERE (`role:user` →
allowlist). Negative: no distinguishing signal — the mechanism may be
present elsewhere or at a different depth (`200` twice, balance once →
dedup at ledger, replay question moves to the key-scope layer). Both
get recorded; only the falsifier closes the cell.

## "How do I know WHICH bound a value is checked against?"

Three bounds exist — UI's, checker's, transform's. Disambiguate:

- UI bound: read from the front-end (`max`, `min` attributes, JS
  clamps) — a suggestion, not a measurement.
- Checker bound: binary-search the rejection — the `id` where `200`
  becomes `400` is the checker's actual bound.
- Transform's reach: compute from `off`, `S`, `w` — the values that
  produce interesting addresses, checked or not.

The interesting `id` is in `[checker_bound, transform_reach]` —
accepted but reaching forbidden addresses.

## "The challenge has no register/cart/redeem — is this skill relevant?"

The alphabet isn't endpoint names — it's mechanisms. A "NAND checker"
challenge is workflow skip (the checker skips validating transform
output), numeric boundary (the index wrap), and trust-in-earlier-step
(the program trusts its own bytes). Read the mechanism into whatever
the challenge's nouns are.

## "When do I stop entirely?"

When `decide.py` says so — every escalation rung spent: `chain_match`,
`reclassify`, `writeup_search`, `novel_plan`, `fanout_sweep`,
`solver_handoff`. A falsified alphabet is data for the kill map
(`knowledge/attempts/`), not a stop.
