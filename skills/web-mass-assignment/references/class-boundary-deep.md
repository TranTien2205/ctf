# Class boundary deep — mass assignment vs every adjacent class

## vs web-logic-flaw — the parent class

Mass assignment is ONE mechanism inside logic-flaw's alphabet — the
binder-coverage cell. The routing rule: file HERE when the bug is
specifically "the binder bound a field the form didn't send"; file
under web-logic-flaw when the bug is workflow-skip, state-replay,
numeric-wrap, or the broader business-rule failure. A bound `role` →
here; a skipped `/step3` request → logic-flaw.

## vs web-idor — access vs field

The line: object ACCESS vs bound FIELD.

- `GET /api/users/9/orders` returning another's order → IDOR (access).
- `PATCH /users/9 {"role":"admin"}` on YOUR OWN id → mass assignment.
- `PATCH /users/9 {"role":"admin"}` on ANOTHER's id → IDOR reaching a
  write — the IDOR is the access violation; the bound `role` is what
  the write does. Both bugs, but the ACCESS is the primary.
- `{"author_id":9}` forging authorship → mass assignment (bound field).
- `?user_id=9` reading another's record → IDOR.

## vs web-prototype-pollution — one object vs every object

The line: YOUR object vs the shared prototype.

- `{"role":"admin"}` → `user.role = "admin"` on YOUR record → mass
  assignment.
- `{"__proto__":{"role":"admin"}}` or `{"constructor":{"prototype":
  {"role":..}}}` → `{}.role` resolves globally → prototype pollution.

The signal: pollution shows the field on EVERY object (a second
untouched object gains `role`); mass assignment shows it on YOUR
object only. `_.merge`/`deepmerge` walking `__proto__` is the shared
mechanism — the reach decides the class.

## vs web-nosqli — field vs operator

The line: a MODEL field vs a QUERY operator.

- `{"role":"admin"}` → binds a model attribute → mass assignment.
- `{"$set":{"role":"admin"}}` or `{"role":{"$ne":null}}` → operator
  reaching the update document → NoSQL injection.

Same field, different layer: mass assignment writes via the ORM;
NoSQLi writes via the query operator. The `web-nosqli` class is the
operator reach; this class is the field reach.

## vs web-auth-session — store vs token

- `role` bound at register → lands in the DB → mass assignment.
- `role` forged in a JWT → forged claim → auth-session (token forgery).
- `role` bound → re-issued JWT carries it → the chain (bind → re-login
  → token carries the claim).

## vs transport classes — the upstream reach

- `X-Role: admin` header bound → rare; if a gateway forwards headers
  into the binder context, the bug is transport (the header reaches
  the binder). The mass-assignment is the downstream consequence.

## The routing decision table

| Observation | The class |
|---|---|
| binder bound an extra model field on own object | **web-mass-assignment** |
| direct object access by id | web-idor |
| `__proto__`/`constructor` pollutes all objects | web-prototype-pollution |
| `$`-operator keys reaching update | web-nosqli |
| step skipped by request | web-logic-flaw |
| forged token claim | web-auth-session |
| header/proxy adding the param | transport class |

## The chain-overlap

Mass assignment is the FIRST link most often: `role:admin` → the admin
binder opens → the admin endpoint's own mass-assignment writes the
flag field. The bound field is rarely the flag; it's the edge reaching
the flag's gate.
