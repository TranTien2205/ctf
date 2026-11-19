# Falsifiers deep — the kill-shot mechanics per layer

`falsifiers.md` gives the table. This module is the layer structure
behind it — WHY each falsifier kills what it kills, and the exceptions
that keep the shape partially alive.

## The falsifier hierarchy

Falsifiers kill at different depths:

| Depth | Falsifier | Kills |
|---|---|---|
| endpoint | `role: user` on read-back | mass assignment on THIS endpoint |
| content-type | `400 unknown field` on JSON | mass assignment on the JSON path |
| binder | strict schema on ALL content-types | mass assignment on the endpoint entirely |
| model | no privileged fields exist | mass assignment on the app |
| mechanism | state machine enforced on every step | workflow skip |
| layer | dedup at ledger | replay at endpoint AND ledger |
| class | every falsifier across the alphabet | the class on this target |

A shallow falsifier (endpoint-level) leaves siblings alive — the
`PATCH` binder, the form path, the nested object. A deep falsifier
(schema-everywhere) closes them all. The skill's falsifiers are keyed
to depth: know which depth fired before deciding what died.

## The read-back falsifier — mechanics

`role=admin` sent, `role: user` read back. What it proves precisely:

- the binder ran (the `200` says the request succeeded),
- the `role` key did not reach the model (the store shows the default).

It does NOT prove:

- `role` is unbindable through nested paths (`{"user":{"role":"admin"}}`
  is a different code path through the same binder — an allowlist on
  top-level keys may not recurse),
- the update binder shares the create allowlist,
- OTHER privileged fields are blocked (`role` allowlisted says nothing
  of `verified`).

The honest reading: mass assignment via flat `role` on `POST /register`
is dead; three adjacent probes remain cheap and legitimate before the
mechanism is declared dead here.

## The state-machine falsifier — mechanics

`302`/`400` to the required step proves the handler checks `pre(t)`
against server-side state. What it does NOT prove:

- every transition checks — the terminal endpoint (`/flag`, `/export`)
  may not participate in the state machine at all;
- the state isn't forgeable — server-side enforcement of a client-
  writable `step` field is enforcement of attacker-supplied state;
- the ordering is total — branch merges ("either step-2a or step-2b")
  may let an optional path satisfy a required one.

## The dedup falsifier — mechanics

`409` on the second POST proves a consumed-marker. Depths:

- key at `(user, code)` → cross-user replay alive;
- key at `(code)` → cross-code replay dead but same-code-different-user
  dead too;
- key at `requestId` → mutated body + same key = first-write-wins probe;
- check-then-set non-atomically → the PARALLEL window is alive —
  race's ground.

## The boundary falsifier — mechanics

`400 must be positive` kills sign boundaries on ONE field. Live after
it: the same field's OTHER boundaries (a sign check doesn't answer
`NaN` — different guard polarity, or `2147483648` — width not sign),
and every OTHER numeric field — `price`, `discount`, `tax` are
independent layers.

## The transform falsifier — mechanics (the Pachinko kill-shot)

Out-of-limit `id` rejected IDENTICALLY to malformed `id` proves the
transform either doesn't run before the check or its output is checked.
Precision:

- it says nothing about OTHER transforms — the decode/coerce/unit
  transforms on other fields are independent hypotheses;
- "identical" is the operative word — ANY difference (status, text,
  timing, a 500) means the value passed the first layer, and the
  falsifier did NOT fire — it became the class signal.

## Falsifier discipline — the record

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" \
  --verdict falsified --class web-logic-flaw \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"user"' --response "$(cat r.json)"
```

Include the depth in `--evidence` where it's non-obvious:
`'"role":"user" — allowlist on POST /register binder'`. The next session
reads whether `PATCH` remains open from the ledger alone.

## The composite falsifier

A mechanism is fully dead only when every depth is closed. The register
binder falsified + the update binder falsified + strict schema on all
content-types + no privileged fields = the model-level falsifier.
That's rare — most apps falsify shallowly, leaving the adjacent probes
worth their cost.
