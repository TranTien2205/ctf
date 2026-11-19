# Class boundary — web-logic-flaw vs its confusable classes

SKILL.md names the confusables: `web-idor` and `web-race-condition`.
`web-mass-assignment` and `web-graphql` also sit adjacent. This module is
the disambiguation — which class owns the probe when two could.

## web-logic-flaw vs web-idor

| Question | logic-flaw | idor |
|---|---|---|
| What's broken? | a *transition* the workflow forbids | an *object access* ownership doesn't gate |
| The probe | skip a step, replay a transition, push a boundary | read/write another user's objectId |
| The state | the object's state moved illegally | the object itself was reached |
| Verbatim evidence | `status: confirmed` without payment | `{"userId": 999}` data returned |

**The overlap**: `objectId=999` inside a business operation. If the bug is
"the endpoint returned another user's order" → IDOR. If the bug is "the
endpoint *applied a transition* to another user's order that my session
shouldn't trigger" → logic-flaw. Access vs transition.

## web-logic-flaw vs web-race-condition

| Question | logic-flaw | race |
|---|---|---|
| What's broken? | a sequence the server permits | a window the server doesn't close |
| The probe | a single, well-ordered request | overlapping requests in a check-use gap |
| Timing | irrelevant — replay works at any speed | essential — the window must be interleaved |
| The baseline | a single request either does or doesn't transition | serial baseline MUST come first |

**The overlap**: "redeem the code twice". Sent serially → logic-flaw
(idempotency missing). Sent in parallel → race (TOCTOU in the
mark-redeemed check). Probe serially FIRST: if serial replay succeeds,
it's logic-flaw and no race machinery is needed — `race_probe`'s serial
baseline discipline exists exactly for this disambiguation.

## web-logic-flaw vs web-mass-assignment

Mass assignment is a *mechanism inside* this skill's alphabet — the
`role=admin`-at-register shape. The classes overlap deliberately:

- The endpoint binds extra fields to a privileged model attribute →
  `web-mass-assignment` (the dedicated class carries the binding taxonomy:
  Rails `attr_accessible`, Laravel `$fillable`, Django `ModelForm`,
  Express object spread).
- The endpoint lets a workflow reach a forbidden *state* regardless of
  field binding → `web-logic-flaw`.

When the `role=admin` probe works, BOTH classes arguably fired — file it
under mass-assignment (the more specific class) and note the logic
dimension in the solve.

## web-logic-flaw vs web-graphql

A GraphQL mutation that skips a workflow step is a logic flaw *reached
through* GraphQL. Route on the transport: if the work is "which mutation
fields exist and what they bind" → `web-graphql`; if the work is "the
mutation executes step 3 without step 2" → `web-logic-flaw`.

## web-logic-flaw vs web-auth-session

Auth-session owns "who is the session" (token forgery, fixation, MFA
gaps). Logic-flaw owns "what the session may do in what order" (privilege
fields at *registration*, skipped MFA *steps*). Setting `role=admin` at
register is logic-flaw/mass-assignment; editing a session JWT's `role`
claim is auth-session.

## The dispatch rule

When two classes fit:

1. Run the **simpler probe first** — a serial replay before a race, a
   read-back before a chain.
2. Record against whichever class the *evidence* names — the verbatim
   forbidden state, not the hoped-for mechanism.
3. Confusion between logic-flaw and its neighbors is cheap to resolve:
   each class's falsifier is different, and the first falsifier that fires
   names the right class by elimination.
