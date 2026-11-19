# Preconditions — what must be true for mass assignment to exist

## The model precondition

The target model must carry a field worth binding — `role`,
`is_admin`, `verified`, `balance`, `plan`, `permissions`. A model
carrying only `username`, `password`, `email` has nothing privileged
to bind — the model falsifier. Check `GET` responses; a narrow model
kills the class before the first probe.

## The binder precondition

At least one endpoint must bind the request body into the model WITHOUT
a field allowlist — `create(req.body)`, `Object.assign`, `setattr`
loop, `fill($request->all())`, `**json`, `[Bind]` absent, or an
allowlist wide enough to include the dangerous field.

## The decision precondition

The bound field must reach a DECISION — a role check, a verify gate,
a totals computation, a plan gate. A stored-but-unread field is a
null result; the decision is what makes the bind a finding.

## The endpoint precondition

At least one body-accepting endpoint must exist — `POST`/`PATCH`/`PUT`.
A read-only app has no binder. `GET`+params reaching a binder is the
edge case.

## The session precondition

You need an account/object to bind onto — register first, then probe
your own record. Never probe another user's object (the IDOR-adjacent
violation).

## The falsifier check

Before probing, the quick falsifiers:

- `GET` shows NO privileged fields → model falsifier;
- `POST` rejects ALL extra keys on ALL content-types → schema falsifier;
- read-back always = control → binder falsifier.

## The scope precondition

Authorized testing only — CTF, lab, or a sanctioned assessment. Never
fire broad field-sweeps on a shared production instance; probe your
own objects, low write concurrency, record counts small (AGENTS.md
safety rules).
