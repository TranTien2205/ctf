# Mechanism alphabet — the business-logic flaw surface

Every business-logic flaw is a rule the application was told and follows
faithfully — the rule itself is wrong. This module names the mechanism
family; each mechanism is a different way the told-rule diverges from the
intended-rule.

## The mechanism map

| Mechanism | The rule that is wrong | The signal |
|---|---|---|
| mass assignment | the model accepts fields the form never sends | extra field in the body changes state |
| workflow skip | the step order is assumed, not enforced | step N+1 reachable before step N |
| state-machine replay | a one-time transition is not one-time | coupon applied twice, vote counted twice |
| numeric boundary | the type permits values the rule forbids | negative quantity, zero price, overflow |
| two-validator gap | two checks disagree on the same boundary | one rejects, the other accepts |
| trust-in-earlier-step | step N+1 uses step N's output unchecked | modified upstream value flows through |
| scaling-after-check | the bounds check runs before the transform | post-transform address out of range |
| role assignment | a privileged field is settable at creation | `role=admin` at register |
| idempotency | a non-idempotent action is repeatable | refund twice, redeem twice |
| unit confusion | two units share one field | currency vs quantity, ms vs s |
| default fallback | a missing field takes an unsafe default | absent `role` defaults to admin |
| inheritance leak | a parent's field is assignable on the child | `__proto__`-shaped binding |
| confirmation skip | the confirm step is optional | destructive action without confirm |
| time assumption | the server trusts client-supplied time | `createdAt`, `expiry` in the body |
| quantity arithmetic | arithmetic on user values is unchecked | `price * qty` overflows or wraps |
| sequence assumption | IDs must increase, but nothing checks | replay an old ID |
| ownership assumption | the object belongs to the session's user | modify another user's object |
| singleton assumption | only one of these should exist | create a second privileged object |
| precondition assumption | the earlier check ran, and passed | call the later endpoint directly |

## The mechanism mechanics

### mass assignment

The model binds every field in the request body — including fields the form
never sends. The rule that is wrong: the binder trusts the body's field set,
not the form's.

The probe: send the form's fields plus one the model has but the form omits.
The confirmation: the extra field changes state — a `role` set, a `balance`
modified, an `isAdmin` flipped.

### workflow skip

The workflow assumes step N ran before step N+1 — but the API does not
enforce the order. The rule that is wrong: the endpoint trusts the sequence,
not the state.

The probe: call step N+1 directly, skipping step N. The confirmation: the
later step accepts — a payment confirmed without a payment initiated, a
flag revealed without the puzzle solved.

### state-machine replay

A transition marked "one-time" is not — the coupon redeems twice, the vote
counts twice, the token replays. The rule that is wrong: the transition
checks "is valid" but not "was used".

The probe: replay the transition. The confirmation: the second application
produces the same effect — the balance doubles, the count increments twice.

### numeric boundary

The type permits values the rule forbids — a `quantity` that is negative, a
`price` that is zero, a `count` that overflows. The rule that is wrong: the
handler trusts the type, not the domain.

The probe: send the forbidden value — `-1`, `0`, `999999999`, `0.0000001`.
The confirmation: the state the rules forbid is reached — a negative total
charged, an overflow that wraps to a low value.

### two-validator gap

Two checks guard the same boundary and disagree — the client-side check
rejects, the server-side check accepts; or the transport validator rejects,
the checker accepts. The rule that is wrong: the two validators are not
the same rule.

The probe: send the value in the gap — past one validator's limit, inside
the other's. The confirmation: one validator rejects, the other accepts —
the disagreement is the surface.

### trust-in-earlier-step

Step N produces a value; step N+1 uses it without re-checking. The rule
that is wrong: the pipeline trusts its own earlier output — and the output
is attacker-shaped.

The probe: modify the upstream value before the downstream step consumes
it. The confirmation: the downstream step acts on the modified value — a
price set upstream charged downstream, a role granted upstream used
downstream.

### scaling-after-check

The bounds check runs on the pre-transform value; the transform scales it
out of range. The Pachinko shape: `index` checked against `<0x1000`, then
inverted/scaled into `0xe000`, then `0xe000+0x2000 & 0xffff` wraps to `0`
— instruction memory.

The probe: pick an index whose post-scaling address lands outside the
checked range. The confirmation: the transformed address reaches memory the
check was meant to exclude — code memory, an adjacent object, a wrapped
region.

### role assignment

A privileged field is assignable at object creation — `role`, `isAdmin`,
`permissions`. The rule that is wrong: the creation endpoint binds every
field including the privileged ones.

The probe: `POST /register {"user": "x", "role": "admin"}`. The
confirmation: the created object carries the privilege — the role is
`admin`, not `user`.

### idempotency

An action that should happen once happens repeatedly — a refund, a redeem,
a transfer. The rule that is wrong: the endpoint does not record that the
action ran.

The probe: send the action twice. The confirmation: the second call
produces the same effect — the refund is issued twice, the code is
redeemed twice.

### unit confusion

Two units share one field — the server reads `amount` as dollars, the
client sent cents; the server reads `duration` as seconds, the client sent
milliseconds. The rule that is wrong: the field has no unit, so both sides
assume different ones.

The probe: send the value in the other unit — `100` for `1.00`, `60000`
for `60`. The confirmation: the server interprets the value in its own
unit — a charge 100x intended, a duration 1000x intended.

### default fallback

A missing field takes an unsafe default — `role` absent defaults to
`admin`, `verified` absent defaults to `true`, `owner` absent defaults to
the first user. The rule that is wrong: the default is permissive, not
restrictive.

The probe: omit the field entirely. The confirmation: the default lands —
the created object carries the permissive default.

### inheritance leak

A parent's field is assignable through the child's binding — the child
model inherits `isAdmin` from the parent, and the child's binder accepts
it. The rule that is wrong: the binder trusts the field name, not the
intended schema.

The probe: send the parent's field in the child's request. The
confirmation: the inherited field is set — the child object carries the
parent's privilege.

### confirmation skip

A destructive action has a confirm step that is optional — the endpoint
accepts the action without the confirmation token. The rule that is wrong:
the endpoint trusts the client to have asked, not the server to have
recorded it.

The probe: send the destructive action without the confirmation. The
confirmation: the action executes — the object is deleted without the
confirm token.

### time assumption

The server trusts client-supplied time — `createdAt`, `expiry`,
`timestamp` in the body. The rule that is wrong: the timestamp is
attacker-controlled.

The probe: send a timestamp in the past or future. The confirmation: the
server accepts it — an expired token is valid, a future-dated record is
created.

### quantity arithmetic

Arithmetic on user values is unchecked — `price * quantity` overflows,
`balance - amount` goes negative, `total + fee` wraps. The rule that is
wrong: the arithmetic assumes positive bounded inputs.

The probe: send the value that overflows or underflows. The confirmation:
the arithmetic produces the forbidden result — a wrapped total, a
negative balance.

### sequence assumption

IDs or sequence numbers must increase — but nothing checks. The rule that
is wrong: the handler trusts the sequence, not the state.

The probe: replay an old ID or an out-of-order sequence. The confirmation:
the handler accepts it — an old transaction is replayed, a stale state is
restored.

### ownership assumption

The object belongs to the session's user — but the handler does not check.
The rule that is wrong: the endpoint trusts the reference, not the
ownership.

The probe: reference another user's object. The confirmation: the handler
acts on it — another user's record is read or modified.

### singleton assumption

Only one of these should exist — but nothing enforces it. The rule that is
wrong: the creation endpoint does not check for an existing instance.

The probe: create a second privileged object — a second admin, a second
flag-holder. The confirmation: the second object exists — the singleton
invariant is broken.

### precondition assumption

An earlier check ran and passed — so the later endpoint skips it. The rule
that is wrong: the endpoint trusts the pipeline, not the check.

The probe: call the later endpoint directly, without the earlier check.
The confirmation: the endpoint accepts — the guarded action runs without
the guard having run.
