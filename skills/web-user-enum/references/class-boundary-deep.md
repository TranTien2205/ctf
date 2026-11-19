# Class boundary (deep) — the full confusable map

## vs `web-auth-session` — the deepest overlap

The boundary is *what is broken*:
- the auth path is UNIFORM but the session/token is forgeable →
  `web-auth-session`
- the auth path DIFFERS by account-existence → `web-user-enum`
- BOTH: a uniform-auth endpoint can still carry a JWT flaw
  (`web-auth-session`) AND a register that leaks (`web-user-enum`) —
  they are different measurements on different functions, not
  contradictory

Chain: enum produces the account; `web-auth-session` attacks its
credential/session. A confirmed `admin` with a forgeable JWT is
`web-auth-session`'s job; confirming `admin` exists is this class's.

## vs `web-logic-flaw` — the workflow boundary

- a reset that returns the token / does not invalidate the session →
  `web-logic-flaw`/`web-auth-session`
- a reset that reveals EXISTENCE (`"no account"` vs a send) →
  `web-user-enum`
- a `role`/`is_admin` param the server binds → `web-mass-assignment`
- an open-registration / workflow-skip → `web-logic-flaw`

The enum measures the existence-oracle; the logic flaw exploits a broken
rule. A confirmed email feeds `web-logic-flaw`'s reset-flow attack.

## vs `web-sqli`/`web-nosqli` — the oracle-vs-injection

- `user=' OR 1=1--` returns a login → `web-sqli`/`web-nosqli` (the oracle
  is the injection bypass/extraction, not the existence)
- `user=admin` returns a different response than `user=zzz` →
  `web-user-enum`

An injection can EXTRACT the whole user table (a stronger primitive);
the enum measures the exists-oracle per-name. Both can fire on the same
field — the injection is `web-sqli`'s; the existence differential is
this class's.

## vs `web-idor` — the object-vs-existence

`GET /api/users/{id}` → `web-idor` (the object is owned/restricted).
The same endpoint's `200`/`404` → `web-user-enum` (the existence
difference). Both can fire; the read-through is `web-idor`, the
existence is this class.

## vs `web-oauth-sso` — the SSO boundary

`account_not_found` on an unlinked email → `web-user-enum` (the oracle).
The SSO auto-link/pre-hijack exploit → `web-oauth-sso`. The enum
confirms the email; the SSO class exploits the link.

## The composite rule

A chain may use both — the enum produces the account, the neighbor
exploits it. Record each as its own class; the chain card names the
class that closed the flag, not every class in the path.
