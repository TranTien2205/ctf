# Per-surface map — the app surfaces and their mechanism density

## Registration / account creation

- mass assignment (the #1 surface), role assignment, singleton
  (second admin), time (self-issued activation), workflow skip
  (register→active without verify).

## Login / session

- Mostly `web-auth-session` ground. Logic overlap: session-fixation as
  trust-in-earlier-step, MFA *step* skipping as workflow skip.

## Cart / order / checkout

- numeric boundary (qty, price, discount, tax, shipping, amount),
  unit confusion (cents/dollars), workflow skip (confirm unpaid),
  trust-in-earlier-step (carried totals), replay (double-confirm),
  ownership (other carts). The densest logic surface in most apps.

## Coupons / redeem / claim / vote / invite

- idempotency + replay (the one-time-action surface), sequence (code
  predictability), cross-user replay, time (expired codes).

## Transfer / withdraw / deposit

- idempotency, numeric boundary (negative transfer = inverse deposit),
  ownership (other `from` account), sequence (nonce replay). A negative
  withdrawal is the canonical "forbidden arithmetic state".

## Profile / update endpoints

- mass assignment via a second binder (the `PATCH` allowlist often
  differs from `register`), ownership, role-carried fields.

## Admin / flag / export / download

- The SINK surface — what chains reach. Direct bare GET is a
  workflow-skip probe (`/flag` may check nothing), but usually the flag
  sits inside a role-gated view.

## API / GraphQL

- Same mechanisms over richer carriers: nested objects, arrays, aliases
  (batch duplicate transitions in one request — a replay variant),
  `additionalProperties` schemas deciding mass assignment.

## Emulators / interpreters / custom runtimes

- scaling-after-check (the Pachinko home), transform gaps, shared
  data/code memory, index-transform arithmetic. Rare in ordinary apps,
  common in CTF logic challenges.

## Webhooks / callbacks

- trust-in-earlier-step (callback authenticity), replay (the same event
  redelivered), sequence (event ordering).
