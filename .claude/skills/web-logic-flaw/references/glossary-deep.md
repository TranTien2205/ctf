# Glossary deep — the terms, with their precise semantics

`glossary.md` is the quick list. This module gives each term its exact
meaning inside this system's machinery.

## allowlist binding

The handler's binder copies only named request fields into the model.
Precise semantics: it's a CHECK-SET on the request's key set —
`K ⊆ F_allowed` — applied at bind time. Falsifier for mass assignment;
depth matters (a depth-1 allowlist leaves nested paths open).

## baseline pair

Two requests differing in exactly one variable — the manipulation —
with both responses recorded verbatim. The evidence atom for every
logic verdict. Not "a normal request": THE SAME request minus the
changed variable.

## boundary alphabet

The canonical probe set for numeric fields. Not "weird numbers" — each
value exercises a NAMED code path: `-1`→sign, `0`→zero, `-0`→signed-
zero, `0.1`→integer-typing, `NaN`→comparison-semantics, `1e309`→float-
overflow, `2147483648`→int32 width, `0x10`→radix coercion, `"1"`→type
coercion. A value is only in the alphabet if it names a path.

## chain card

`knowledge/chains/<id>.json` — a verified solve's record: `signals`,
`chain[]`, `first_confirming_probe`, `blast_radius`, `field_notes`.
Semantics: a CANDIDATE shape for a new target — a literal signal match
is a gradable lead; `family_leads` (prose-vocabulary match) is weak and
read-only; neither is a finding.

## consumed marker

The store-side bit making a one-time action idempotent —
`code.used = true`. Its scope (`(code)` / `(user,code)` / `requestId`)
and atomicity (check-and-set vs separate writes) are the replay
mechanism's real boundary.

## different-layer rejection

Two rejected values producing DIFFERENT rejection shapes (status, text,
timing). Semantics: the values died at different pipeline layers — the
second value passed the layer that rejected the first. The transform-
gap class signal; identical rejections are its falsifier.

## echo

The write-response reflecting sent fields. Semantics: proves PARSING,
not STORAGE — `{"role":"admin"}` echoed means the server saw the key;
the read-back decides whether the binder wrote it. Echo-vs-read-back
diffs are the mass-assignment evidence primitive.

## falsifier

A probe result that closes a hypothesis — with DEPTH: endpoint-falsifier
(one binder), content-type falsifier (one parser path), mechanism
falsifier (the whole mechanism), class falsifier (the whole alphabet).
The ledger records the depth so the next probe knows what died.

## impossible pair

Two response fields that can't legitimately co-exist —
`confirmed:true` + `paid:false`. The workflow-skip evidence primitive:
one field proves the transition ran, the other proves its precondition
didn't.

## imagined workflow / implemented state machine

`L` (the intended sequence language) vs `L'` (what the handlers accept).
A logic flaw is a word `w ∈ L' \ L`. The class's whole formal frame —
see `theory-deep.md`.

## mechanism alphabet

This skill's cover of `L' \ L`: 13 named mechanism cells (mass
assignment, workflow skip, state replay, numeric boundary, scaling-
after-check, unit confusion, role assignment, idempotency, time,
sequence, ownership, singleton, trust). Each cell has its probe grammar
and falsifier; the sweep order is cheapest-first.

## negative result

A probe with no distinguishing signal — bounds mechanism location
without closing it. Not a falsifier: `200`+deduped is a negative that
relocates the question to the ledger layer.

## read-back

A fresh GET on the mutated object — the store's truth vs the write's
echo. The evidence primitive for every write-shaped probe.

## rejection stack

The ordered layers a request can die at: transport/schema → binder →
field validator → state machine → ledger/dedup → sink. Bucket
rejections by shape to map which layer answered — the different-layer
signal depends on it.

## serial baseline

The sequential replay that must run before any parallel window is
considered — a signature that appears serially is not a race. Shared
discipline with `web-race-condition`; the serial `409` is what routes
the question across the class boundary.

## soft no-op

A `200` response on a failed precondition where the handler does
nothing — looks like a skip, isn't. The read-back (unchanged state)
distinguishes it: `200` ≠ forbidden state.

## transform

Any arithmetic between check and use: `off + id*S`, scale, decode,
coerce, unit-convert, duplicate-key resolution. The checker bounds the
input; the sink consumes the output; the gap is where they disagree.
The generalized Pachinko invariant.
