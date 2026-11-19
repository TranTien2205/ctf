# Class boundary — mass assignment vs the confusable classes

## vs web-logic-flaw

Mass assignment is ONE mechanism inside the logic-flaw alphabet — the
binder-coverage cell. File here when the bug is specifically "the
binder bound a field the form didn't send"; file under web-logic-flaw
when the bug is workflow-skip, state-replay, numeric-wrap, or any other
letter of the alphabet. A `role` field bound at register → here; a
step skipped by calling `/step3` directly → logic-flaw.

## vs web-idor

The line: ACCESS vs FIELD.

- `/api/users/9/orders` returning another user's order — the BUG is
  object access → IDOR.
- `POST /notes {"author_id":9}` forging authorship — the BUG is the
  bound field → mass assignment.
- `PATCH /users/9 {"role":"admin"}` on YOUR OWN id → mass assignment;
  on ANOTHER user's id → IDOR reaching a write (both — the IDOR is the
  access, the bound role is the write).

## vs web-prototype-pollution

The line: ONE object vs EVERY object.

- `{"role":"admin"}` writing a property on YOUR user object → mass
  assignment.
- `{"__proto__":{"role":"admin"}}` or `{"constructor":{"prototype":
  {"role":..}}}` writing on the shared prototype — every object gains
  the property → prototype pollution. The signal: `{}.role` resolves
  globally, a second untouched object shows the field. Different class,
  different evidence — route there.

## vs web-request-smuggling / web-host-header

Not confusable — those are transport-layer. If a header/proxy rewriting
adds a `role` param the app binds, the bug is transport (file there);
the mass-assignment is the downstream CONSEQUENCE.

## vs web-auth-session

`role` bound at register vs `role` forged in a JWT — the former writes
the model, the latter forges the token. A bound `role` that lands in a
RE-ISSUED token is the chain (bind → next login's JWT carries it);
forging the token directly is auth-session.

## vs web-sqli / injection classes

An UPDATE endpoint forwarding extra keys to the update document is
operator injection (nosqli) when the KEYS are operators
(`{$set:{role:..}}`); mass assignment when the keys are model fields.
`"role":"admin"` → here; `"$set":{"role":"admin"}` → nosqli.

## The routing table

| Observation | Class |
|---|---|
| binder bound an extra model field | **web-mass-assignment** |
| direct object access by id | web-idor |
| prototype polluted for all objects | web-prototype-pollution |
| workflow step skipped by request | web-logic-flaw |
| `$`-operator keys reaching update | web-nosqli |
| forged token claims | web-auth-session |
| header/proxy adding the param | transport class |

## The chain-overlap

Mass assignment is frequently the FIRST link: `role:admin` bound →
the admin binder opens → the admin endpoint's own mass-assignment
writes the flag field. Or `verified:true` bound → the verify-gated
flag route opens. The bound field is rarely the flag itself; it's the
edge that reaches the flag's gate.
