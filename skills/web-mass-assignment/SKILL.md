---
name: web-mass-assignment
description: >
  Action-oriented depth skill for Mass assignment / parameter binding. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-logic-flaw, web-idor.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, mass-assignment, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Mass assignment / parameter binding

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

repeat the legitimate request with one extra field the client never sends (role, is_admin, balance, discount) — then read the affected object back

**Falsifier** — the observation that closes this class: the server ignores or rejects every undocumented field: the stored object is byte-identical to the control submission
## Recognise

The handler binds the request body straight into a model. Registers, profile
updates, orders and checkout forms are the usual shapes — anywhere a JSON or
form payload is deserialized into an object that carries fields the form never
renders: `role`, `is_admin`, `balance`, `price`, `status`.

## Confirm safely

Send the legitimate request twice: once verbatim (control), once with ONE extra
field. Then read the object back through a GET or a later response. The field
stored or honoured is the confirmation — not the 200.

Only ever send fields whose semantics you can predict; a wrong type or a
server-internal field can corrupt the object or the challenge state.

## Carriers that matter

| Carrier | Shape |
|---|---|
| JSON body | `{"user":"x","role":"admin"}` merged over defaults |
| Form body | `role=admin` appended alongside declared fields |
| Nested object | `{"billing":{"discount":100}}` — server-side merge reaches deep fields |
| Array / repeated key | `role=user&role=admin` — binder picks first or last |

`constructor.prototype`-style keys are NOT mass assignment — they pollute the
prototype for every object; that is web-prototype-pollution.

## Traps

- A stored field that is never read anywhere is not a finding — prove the bound
  field changes a decision (price, privilege, approval) before citing it.
- Some frameworks bind form fields only when named with a model prefix
  (`user[role]`); try the unprefixed and the prefixed name before concluding.
- Read-back matters: a field accepted but discarded by the serializer is a
  null result. Record it honestly.

## Operational probe

```bash
curl -i -X POST -H 'Content-Type: application/json'   -d '{"username":"me","password":"x","role":"admin"}' "$BASE/api/register"
curl -i "$BASE/api/me"   # read back: is role honoured?
```

`tools/web/binding_probe.py` runs the field matrix: one extra field at a
time (`role`, `admin`, `is_admin`, `isAdmin`, `debug`, `permissions`,
`group`, `verified`, `is_staff`, or `--fields`) with a canary value,
then grades whether it echoed in the response or landed on `--readback`.
A landed field is a candidate; whether it changes authorization is the
confirm above.

## Routing

Shares signals with: `../web-logic-flaw/`, `../web-idor/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/web-mass-assignment/references/README.md`
- `skills/web-mass-assignment/references/binding-shapes.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
