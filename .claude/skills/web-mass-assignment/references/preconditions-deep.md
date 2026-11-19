# Preconditions deep — every condition mass assignment needs

## Condition 1 — a writable model with privileged fields

The target model must carry a field worth binding: `role`, `is_admin`,
`verified`, `balance`, `plan`, `permissions`, `price`. A model with
only `username`, `password`, `email` has nothing to escalate — the
model falsifier. Check `GET` responses, the bundle, error messages,
docs for the privileged fields.

## Condition 2 — a binder that reaches it

At least one endpoint must bind the request body into the model —
`POST`/`PATCH`/`PUT`/`import`/GraphQL. The binder's coverage must
exceed the form's declared fields:

- `create(req.body)` / `Object.assign` / `setattr` loop — absent allowlist;
- `permit(:name,:bio,:role)` — the allowlist INCLUDES the dangerous field;
- `**json` with a wide signature — the signature admits the field;
- `_.merge`/`deepmerge` — nested tunnels reach through the parent.

## Condition 3 — a decision that reads the field

The bound field must reach a DECISION — a role check, a verify gate,
a totals computation, a plan gate. `check_admin()` reading `user.role`,
`totals()` reading `order.price`, `verified_required()` reading
`user.verified`. A stored-but-unread field is a null result.

## Condition 4 — an object you own

A record to bind onto — your account, your order, your profile.
Never probe another user's object (the IDOR-adjacent violation);
register first, probe your own `me`/`id`.

## Condition 5 — a reachable read-back or decision

Evidence needs either:
- a `GET` returning the stored field (the read-back), OR
- a gated route whose `200`/`403` proves the decision.

If neither exists (serializer-hidden + no observable gate), the field
is unprovable — a different surface.

## Condition 6 — the scope

Authorized testing only — CTF, lab, sanctioned assessment. No broad
field-sweeps on shared production; low write concurrency; test on
your own objects; record counts small (AGENTS.md safety rules).

## The falsifier check — when none of these hold

- no privileged fields in ANY model → class dead;
- ALL content-types reject extras (`400` everywhere) → parser dead;
- ALL binders drop extras (`200`+drop everywhere) → binder-family dead;
- stored field changes NO decision → inert, not a finding;
- endpoint unreachable (`403` ownership) → wrong object, not this class.

## The precondition matrix

| If missing... | The state |
|---|---|
| privileged fields | model falsifier — class dead |
| a binder reaching them | endpoint falsifier — no surface |
| a decision reading them | inert — null result |
| an ownable object | wrong scope — probe `me` |
| read-back + decision | unprovable — different surface |
| authorization | out of scope — stop |
