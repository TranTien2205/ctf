# Per-boundary — each class-boundary call, decided

## `web-user-enum` vs `web-auth-session`

| The observed | The class |
|---|---|
| a uniform-auth + a forgeable JWT/session | `web-auth-session` |
| a differential on account-existence | `web-user-enum` |
| a confirmed name + its weak pw | enum → `web-auth-session` |
| a reset-token flaw | `web-auth-session`/`web-logic-flaw` |

Decide by *what is broken*: the existence-oracle is enum; the
credential/session is auth-session. They chain — enum names the account,
auth-session attacks it.

## `web-user-enum` vs `web-logic-flaw`

| The observed | The class |
|---|---|
| a skipped workflow/replayed state | `web-logic-flaw` |
| an existence leak on the username | `web-user-enum` |
| a reset that returns the token | `web-logic-flaw`/`web-auth-session` |
| a `role`/`is_admin` bound param | `web-mass-assignment` |

## `web-user-enum` vs `web-sqli`/`web-nosqli`

| The observed | The class |
|---|---|
| a `' OR 1=1`/`{"$ne"}` injection oracle | `web-sqli`/`web-nosqli` |
| a `user=admin` vs `user=zzz` existence diff | `web-user-enum` |

The injection EXTRACTS (a stronger primitive); the enum measures the
exists-oracle. An `admin'` that returns a login page is `web-sqli`; a
`admin` that returns a different error than `zzz` is `web-user-enum`.

## `web-user-enum` vs `web-idor`

| The observed | The class |
|---|---|
| `GET /api/users/{id}` returns a user object | `web-idor` |
| the same endpoint `200`/`404` by existence | `web-user-enum` |

Both fire on one endpoint — the read-through is `web-idor`, the
existence is `web-user-enum`.

## `web-user-enum` vs `web-oauth-sso`

| The observed | The class |
|---|---|
| `account_not_found` on an unlinked email | `web-user-enum` |
| the SSO auto-link/pre-hijack exploit | `web-oauth-sso` |

The enum confirms the email exists; the SSO class exploits the link.

## The composite rule

A chain uses both — enum produces the name, the neighbor exploits it.
Record each as its own class; the card names the flag-closing class,
with `web-user-enum` as the recon that surfaced the target.
