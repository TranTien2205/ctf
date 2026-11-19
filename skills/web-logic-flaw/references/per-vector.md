# Per-vector map — the transport carriers and which mechanisms ride them

## JSON body

The richest carrier — object semantics open the binder variants.

- **mass assignment**: flat fields + nested (`{"user":{"role":"admin"}}`)
  + arrays (`{"role":["admin"]}`) + constructor paths.
- **numeric boundary**: JSON numbers lose precision past 2^53 at parse —
  the float gap exists before the checker runs.
- **duplicate keys**: `{"role":"user","role":"admin"}` — last-wins in
  most parsers; a validator reading the first and a binder taking the
  last is the parse-layer validator gap.
- **type confusion**: `{"qty":"1"}`, `{"qty":[1]}`, `{"qty":{"$gt":0}}` —
  each reaches different coercion paths (the object-typed value borders
  `web-nosqli` territory).

## Form-encoded body

Scalar-only, but the duplicate-param gap is the form version of
duplicate-key:

```
role=user&role=admin        qs libraries: last / first / array
step=1&step=3               same question at the workflow layer
qty=-1&qty=1                which reaches the arithmetic?
```

- **workflow skip**: `step`/`state`/`token` params.
- **numeric boundary**: string-typed numbers — `"1,000"`, `"0x10"`,
  `"+1"` — the coercion paths differ from JSON numbers.

## Query string

Same scalar surface as form bodies, plus: GET endpoints carrying state
transitions (a `/redeem?code=X` GET is itself a workflow bug — prefetch
and CSRF ride it).

- **replay**: URL-logged idempotency keys.
- **boundary**: `?qty=-1` — same alphabet, string transport.

## Cookies

The state machine's writable record:

- **workflow skip**: `step=3`, `state=confirmed`, `verified=true` cookies.
- **trust-in-earlier-step**: `price=`, `cart=` values minted into cookies
  and trusted back.
- Unsigned cookies forge directly; signed ones need `session_dissect`
  first — a signed-cookie state bit is an auth-session question.

## Headers

- **trust-in-earlier-step**: `Referer`, `Origin`, `X-Forwarded-For`,
  `X-Real-IP` consulted at boundaries (the proxy-vs-app disagreement is
  `web-parser-differential`).
- **idempotency**: `Idempotency-Key` — same key+mutated body is the
  first-write-wins probe.

## Path segments

- **ownership**: `/order/999`, `/user/1` — IDOR-adjacent; the transition
  version (`POST /order/999/confirm`) stays logic-flaw.
- **workflow**: `/checkout/step3`, `/flow/confirm` — path-carried steps
  skip like param-carried ones.

## Method and content-type

- **GET on a transition** — a read-only verb triggering a state change is
  itself the bug (CSRF/prefetch-able transitions).
- **`PATCH`/`PUT` vs `POST`** — the update binder often differs from the
  create binder; mass assignment probes repeat per method.
- **content-type confusion** — the endpoint parses both form and JSON;
  a field the JSON schema allowlists may slip through the form path.
