# Theory deep — the formal frame for business-logic flaws

## The state-machine formalization

An application is a transition system `(S, Σ, δ)`:

- `S` — states: the set of all reachable configurations (users, orders,
  balances, flags).
- `Σ` — the alphabet of requests.
- `δ : S × Σ → S` — the transitions the handlers implement.

The developer *imagines* a sub-language `L ⊂ Σ*` — the valid request
sequences. The implemented system accepts a larger language `L' ⊃ L`. A
business-logic flaw is a word `w ∈ L' \ L`: a sequence the code accepts
that the design forbids.

This is why the class resists payload lists: the flaw is a *property of
the sequence*, and the alphabet of sequences is infinite. The mechanism
alphabet bounds the search by naming which SINGLE deviations to test —
an extra field (Σ the form doesn't use), a missing element (skipped
step), a repeated element (replay), a boundary value (Σ's numeric
edges), a reordered sequence.

## The four invariants that break

Every logic flaw violates one of four invariants:

### 1. Field conservation — "only declared fields bind"

The model `M` has fields `F`; the form declares `F_declared ⊂ F`. The
binder maps request keys `K` into `F`. Flaw: `K ∩ (F \ F_declared) ≠ ∅`
reaches the model. The check that should exist — `K ⊆ F_declared` — is
the allowlist. Its absence is mass assignment.

### 2. Ordering — "transitions happen in order"

The intended order is a partial order `≺` on transitions. The handler
for transition `t` checks `pre(t)` — its declared preconditions. Flaw:
`pre(t)` in code is weaker than `≺` requires — `confirm` checks `order
exists`, not `paid`. The gap between checked-precondition and
required-precondition is the skipped edge.

### 3. Uniqueness — "each effect happens once"

For one-time transitions `t`, there must exist a consumed marker `c(t)`
checked-and-set atomically. Flaw: no `c(t)` (replay works serially) or
`c(t)` not atomic (TOCTOU — `web-race-condition`) or `c` keyed on the
wrong scope (cross-user replay).

### 4. Value integrity — "the value used is the value checked"

A value `v` is checked (`check(v)`) then transformed (`v' = T(v)`) and
used (`sink(v')`). Flaw: `check`'s domain ≠ `T`'s range — the
transform produces values outside the checked set. Pachinko: `check(id <
LIMIT)`, `T = off + id*S mod 2^w`, `sink = mem[T]`. The reachable
`T(id)` for `id ∈ [0, LIMIT)` exceeded the memory region the check
intended to protect — including instruction memory.

This fourth invariant is the deepest: it covers scaling, unit
conversion, decode, coercion, and duplicate-key parsing — every case
where two components hold different models of the same value.

## Why "the UI bounds it" is never a check

The UI constraint lives client-side; `δ` runs server-side. The
implemented system `L'` includes every request the SERVER accepts —
client validation modifies `L` (the imagined language) not `L'`. Every
"the form prevents it" observation is a claim about `L`, and the probe
tests `L'` directly.

## The layered-rejection corollary

Rejections come from layers: schema → binder → validator → state →
ledger → sink. A probe rejected at layer `i` never measures layers
`j > i`. The contrast probe (malformed vs out-of-limit) identifies `i`:
identical rejections → same layer; different → the second value passed
layer `i` and died at `j`. Pachinko's different-layer rejection was the
measurement that the transform ran before the check — `j` rejected
where `i` had passed.

## Composition and the flag

Flags sit at states `s_flag ∈ S` reachable only through `w ∈ L' \ L`.
Single-edge flaws rarely reach `s_flag` directly — the verified cards
compose edges: privileged field → role state → admin transition → flag
state. The chain card records the whole `w`; the solve reconstructs it
edge by edge, each edge carrying its own confirm and falsifier.

## The budget as a formal bound

The mechanism alphabet is a cover of `L' \ L` — finite because the
deviation TYPES are finite even though `Σ*` is infinite. Five probes
per mechanism × ~13 mechanisms bounds the sweep; a falsifier closes a
whole cover-cell at once. `decide.py` enforces the bound because agents
don't — the Polynomial lesson was a session spent inside one cell.
