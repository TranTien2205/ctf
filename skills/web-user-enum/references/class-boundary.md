# Class boundary — vs the confusable neighbors

## vs `web-auth-session`

The session/token is the bug (a forgeable JWT, a weak secret, a session
fixation, a reset-token flaw) → `web-auth-session`. An existence ORACLE
on an account endpoint → `web-user-enum`. The classes chain — enum
produces the account that `web-auth-session` attacks. A clean
`"invalid credentials"` with no differential is closed for enum; a JWT
flaw on the same endpoint is `web-auth-session`.

## vs `web-logic-flaw`

A broken business RULE (skip a workflow step, replay a state, a price/
balance manipulation) → `web-logic-flaw`. An existence LEAK on the
username field → `web-user-enum`. A reset-flow that returns the token is
`web-logic-flaw`/`web-auth-session`; a reset that reveals existence is
`web-user-enum`. The account-list output feeds `web-logic-flaw`'s
victim targeting.

## vs `web-sqli` / `web-nosqli`

The username field carries an injection payload → `web-sqli`/`web-nosqli`
(the oracle is the injection — a `'` error, a `true`/`false` SQL
boolean, a `$ne` bypass). The username field carries a candidate NAME
and the response differs by existence → `web-user-enum`. An injection
can EXTRACT the user list (a stronger primitive); the enum measures the
existence-oracle, not the extraction.

## vs `web-idor`

`GET /api/users/{id}` returning a user object → `web-idor` (the object
is owned/restricted). The same endpoint `200`/`404` revealing existence
→ `web-user-enum`. The read-through is `web-idor`; the existence
difference is `web-user-enum` — both can fire on one endpoint.

## vs `web-oauth-sso`

An SSO flow that leaks account-exists (`account_not_found` on an
unlinked email) → both fire; the SSO-collision/pre-hijack exploit is
`web-oauth-sso`, the existence-oracle is `web-user-enum`.

## The routing rule

Measure the existence oracle HERE; route the EXPLOIT it feeds to the
neighbor. The classes chain, not overlap — a confirmed account name is
`web-user-enum`'s output and the neighbor's input.
