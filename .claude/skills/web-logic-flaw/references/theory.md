# Theory — why business-logic flaws exist

## The security model is implicit

Injection flaws live in code — a string reaches a sink. Logic flaws live
in the **gap between the workflow the developer imagined and the state
machine the code permits**. The imagined workflow is a line; the
implemented one is a graph. Every edge in the graph that isn't on the
line is a potential logic flaw.

```
imagined:   register → verify → pay → confirm → flag
implemented: a set of handlers that each check SOME precondition
```

The flaw is never "a missing check" in the abstract — it is a specific
edge: `/confirm` runs without checking `paid=true`, because the check
lived in the *UI flow* (you can't click confirm before paying) rather
than the handler.

## The four structural causes

### 1. Validation at the wrong layer

A value is checked where it enters, used where it's transformed. The
check reads `id`; the sink computes `off + id*S`. Pachinko: the bounds
check was on the raw index, the memory write on the transformed address —
and the transform's range exceeded the checker's intent. Any transform
between check and use — scaling, decoding, unit conversion, coercion —
is a candidate gap. **Check the value the sink uses, not the value the
user sent.**

### 2. State distributed across trust boundaries

The workflow's state lives partly client-side (a `step` param, a `price`
in a hidden field, a cookie's `verified` flag) and partly server-side.
Any state bit readable or writable by the client is a bit the attacker
controls. The fix is always "server recomputes" — the flaw is that it
doesn't.

### 3. Missing uniqueness and idempotency

Every action that should happen once — redeem, refund, vote, claim —
needs a uniqueness mechanism: a consumed marker, a dedup key, a
transaction. The default is *no* mechanism, because nothing in the happy
path demands one. Replay works until someone builds the dedup — and
nobody builds it, because it isn't in the demo.

### 4. The model is wider than the form

The framework binds request fields to a model object. The model has
`role`, `balance`, `verified`; the form sends `username`, `password`.
Whatever the binder does with extra fields decides mass assignment:
merge-and-bind → flaw; allowlist → safe. The bug is a **default** —
binding everything is the convenient default, allowlisting requires an
explicit decision.

## Why automation misses them

A scanner asks "does this input reach a sink?" A logic flaw asks "does
this sequence of valid requests reach a forbidden state?" — a question
about the *composition* of individually-correct handlers. Each request is
well-formed; only the sequence is wrong. Detection requires a model of
what the workflow *should* forbid — which is why the skill's first probe
is "one extra field" or "one skipped step": the smallest deviation from
the imagined path.

## The budget connection

Logic flaws resist enumeration — there's no payload list to exhaust. The
mechanism alphabet bounds the search: field-binding, ordering, replay,
boundaries, transforms. Each mechanism has a falsifier, each falsifier
kills a layer. The discipline is the same as every other class: measure,
record, change layers on a falsifier — never re-spell a dead probe.
