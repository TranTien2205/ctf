# Negative results deep — the kill-map format and its rules

## The cell-addressed negative

A mass-assignment negative isn't "the class is dead" — it's "THIS cell
is dead." The cell address is `(endpoint, carrier, content-type,
method, field-semantic)`. Recording the cell closes it; the matrix
shows which cells remain live.

## The record format

```
## POST /register — endpoint falsifier (depth 2)
- control `{"u":"c1","p":"x"}` → /api/me `{"role":"user"}`
- canary `+"role":"admin"`     → /api/me `{"role":"user"}`  byte-identical
- carrier: json/flat;  method: POST;  field: privilege semantic
- verdict: binder dropped the flat extra — allowlist in this route
- live cells: PATCH /me (json), POST /register (form), nested tunnel
```

## The five negative types

| Type | Signature | Record |
|---|---|---|
| schema rejection | `400/422 unknown property` | content-type cell dead |
| endpoint drop | `200` + read-back = control | endpoint's flat cell dead |
| binder-family drop | drop on all carriers+methods | binders dead; /import/GraphQL live |
| model absence | no privileged fields anywhere | class dead on this app |
| inert field | stored, gate unchanged | field dead; next semantic |

## The attribution rule

A negative is only valid against a CONTROL:

- canary `role:"admin"` → read-back `role:"user"` is the falsifier ONLY
  because the control also showed `role:"user"`;
- a canary-only `role:"user"` is ambiguous — `user` could be the
  default OR the drop's product;
- two fields in one canary → the diff can't be attributed; split.

## The live-cell map

```
endpoint         carrier      flat     nested   array   typed
POST /register   json         DEAD     live     live    live
POST /register   form         DEAD     —        live    —
PATCH /users/me  json         live     live     live    live
PATCH /users/me  form         live     live     live    live
PUT  /users/:id  json         live     live     live    live
POST /orders     json         live     live     live    live
/import          json         live     live     live    live
GraphQL          args         live     input-obj —      —
```

The map is the honest state: `DEAD` cells are spent, `live` cells are
the next probes.

## The inert-field record

```
PATCH /users/me {"role":"admin"} → stored ("role":"admin" on /api/me)
GET /admin → 403 identical to control session
verdict: INERT — gate reads elsewhere; next semantic: is_staff,
permissions, or the JWT-re-issue edge
```

Inert is not dead — the binder binds; the FIELD was wrong.

## The serializer-hidden caution

Field stored, never returned — the `GET` can't confirm. Record "stored,
serializer-hidden" and exercise the decision directly; don't falsify
on read-back absence alone.

## The negative's value

A recorded falsifier saves the next session from re-walking the cell —
the kill map is as valuable as a solve path. The depth annotation
(`endpoint` vs `binder-family` vs `model`) is what makes the map
honest: it says which cells are PROVABLY dead vs which are untested.
