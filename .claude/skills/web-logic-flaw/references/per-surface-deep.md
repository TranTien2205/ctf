# Per-surface deep — the surface internals and their mechanism density

`per-surface.md` tabulated surfaces. This module reads what's behind
each surface — the code shapes and the probes they demand.

## The registration surface

What ships: a form → `Model.create`. The probes:

```
flat:      {"role":"admin"}
nested:    {"user":{"role":"admin"}}, {"profile":{"role":"admin"}},
           {"meta":{"verified":true}}
array:     {"role":["admin"]}, {"permissions":["*"]}
dotted:    user.role=admin, user[role]=admin (form encoding)
dup:       {"role":"user","role":"admin"}, ?role=user&role=admin
proto:     __proto__[role]=admin, constructor.prototype.role=admin
```

Each is a different binder code path — the flat falsifier leaves the
others open at one probe each.

## The checkout surface

The arithmetic surface — `qty`, `price`, `discount`, `tax`, `shipping`,
`total`, `amount`, `currency`, `unit`. Per field the boundary alphabet;
per pair the arithmetic consistency:

- `qty=-1` on `price` vs `quantity` — independent validators.
- `discount > price` — a total that goes negative through the discount
  leg.
- `currency=X` mismatched to `amount` — the unit-confusion home.

## The one-time-action surface

`redeem`, `claim`, `refund`, `vote`, `invite`, `reset`. The dedup
taxonomy:

```
no marker              → serial replay works
marker set late        → check-then-set window (race)
marker scoped (user)   → cross-user replay
marker scoped (key)    → same-key-mutated-body
marker at ledger       → endpoint replays, ledger dedups (silent)
```

The serial probe is the cheapest discriminator: `200`+effect twice →
no marker; `409` → marker at endpoint; `200` twice + effect once →
marker at ledger.

## The update surface

`PATCH`/`PUT` on the profile — the second binder. `register`'s falsifier
doesn't apply: update handlers often merge wider (the profile is meant
to be editable — the allowlist covers display fields, the model carries
`role` too). Also the method-override paths: `POST` + `_method=PUT`,
`X-HTTP-Method-Override`.

## The terminal surface

`/flag`, `/admin`, `/export`, `/download`. Zero-cost bare probes first —
they may check nothing, a client-carried bit (`session.completed`), or
a role. Each check type maps back to the edge that satisfies it.

## The index surface

Emulators, record accessors, paginated views — anywhere `id`/`offset`/
`page`/`index` becomes an address. The transform questions: is the
index checked before or after `off + id*S`? Is the word-width `w` the
index width or the address width? Does the transformed address share
space with code (interpreters) or privileged objects (adjacent records)?

## The callback surface

Webhooks, payment confirmations, OAuth callbacks — server→server
transitions whose authenticity is the trust-in-earlier-step question:
does the callback verify origin, or does a client-forged "payment
complete" flip the `paid` bit?
