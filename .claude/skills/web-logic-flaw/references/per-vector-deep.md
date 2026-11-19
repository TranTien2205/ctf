# Per-vector deep — the carrier internals, one per transport

`per-vector.md` mapped carriers to mechanisms. This module is the
carrier internals — how each transport delivers a logic value and which
parser path decides what the binder sees.

## JSON body — the deep read

The JSON parser runs before the binder. Three parse-layer facts decide
which value arrives:

1. **Duplicate keys**: `{"role":"user","role":"admin"}` — virtually
   every parser takes the LAST key. A validator reading the first
   occurrence and a binder applying the last is a two-validator gap at
   the parse layer.
2. **Number precision**: `9007199254740993` parses to `...992` in JS
   doubles — the checker's `id <= 9007199254740993` compares a number
   the request never contained.
3. **Type freedom**: `{"qty":"1"}`, `{"qty":[1]}`, `{"qty":{}}` — the
   binder's coercion path, not the parser, decides. `{"qty":{"$gt":0}}`
   crosses toward `web-nosqli` (object-valued params).

## Form body — the deep read

```
role=user&role=admin
```

qs-style parsers deliver `['user','admin']` (array), last-wins parsers
`'admin'`, first-wins `'user'`. The binder's `params[:role]` sees
whatever the parser's convention produced — send duplicates, then read
which won. Nested conventions (`user[role]=admin`, `user.role=admin`)
reach nested model paths flat keys can't.

Scalar-only transport: `NaN`, `Infinity`, `0x10` arrive as STRINGS —
the coercion decides, and coercion paths are the boundary alphabet's
whole point.

## Query string — the deep read

Same parser semantics as form bodies, plus: GET requests on transitions
(`/redeem?code=X`) are themselves a logic flaw — prefetchers and
crawlers walk GETs. A GET-transition endpoint is the workflow bug AND
the CSRF surface.

## Cookies — the deep read

State in cookies splits three ways:

- **unsigned/plain**: `step=3`, `state=confirmed`, `verified=true` —
  direct forge.
- **signed (itsdangerous/JWT/etc)**: readable, not forgeable without
  the key — `session_dissect` names the format; a weak-key recovery is
  an auth-session move.
- **server-side session keyed by cookie**: the cookie is an ID, the
  state is real — the falsifier's home. The remaining question is
  session-fixation / shared-session bleed.

## Headers — the deep read

```
Referer: <step-url>          Origin: <expected>
X-Forwarded-For: <trusted>   X-Real-IP: 127.0.0.1
X-Step: 3                    X-State: confirmed
```

Boundary checks on headers are client-set by definition — the question
is whether the check is the ONLY gate. The proxy-vs-app disagreement
(a proxy stripping/re-writing `X-Real-IP` before the app reads it) is
`web-parser-differential`'s ground; a header the app reads with no
proxy in front is a direct forge.

## Path — the deep read

`/order/999/confirm` — the object in the path, the transition in the
suffix. Two checks may live here: object ownership (IDOR's question)
and transition precondition (logic's). `GET /order/999` 403s while
`POST /order/999/confirm` succeeds — read-path and transition-path
checks are different code.

## Method — the deep read

The same URL on different methods hits different handlers — each with
its own binder and checks:

- `PATCH`/`PUT` — the update binder (wider, usually);
- `GET` on a transition — read-verb state change;
- `_method=PUT`, `X-HTTP-Method-Override` — framework override routing
  POST's validation through PUT's handler.

## The carrier-selection rule

For every logic probe, ask: which carrier does this value travel on,
and does another carrier reach the same sink? A `role` the JSON schema
rejects may bind through `multipart` or form parsers; a `step` the body
validator rejects may be read from the cookie. The alphabet repeats per
carrier — cheaply, because each is one curl.
