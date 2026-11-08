# OAuth/SSO flow abuse

The flag in an OAuth class is almost never crypto — it is a *flow* gap: a
registration, redirect, or token step that trusts something the client
controls.

## Registration race / account pre-creation (SSOS)

A bot or SSO flow assumes a fixed account does not exist yet — because the
intended step creates it. Hammering the register endpoint first binds the fixed
identity to *your* password:

```text
POST /api/register  {"user":"<fixed-bot-account>","password":"<yours>"}
```

Expected: a `200` returned before the bot reaches its own `registerUser` step —
the later flow now operates on an account you hold credentials for, and every
artifact it produces (cookie swap, session, token) lands in your hands.
Falsifier: registration refuses the existing/fixed identity — the flow checks
first or the identity is provisioned elsewhere.

## Tenant and redirect-uri manipulation (SOS or SSO)

Call the login-initiation endpoint for a built-in tenant and read the URL it
returns — the redirect target is the surface:

```text
GET /login?tenant=<builtin>
-> {"redirect": "https://idp/authorize?client_id=..&redirect_uri=.."}
```

The redirect-uri alphabet, in order of what usually survives:

| Shape | Idea |
|---|---|
| `redirect_uri=https://target.evil` | open redirect to your collector |
| `redirect_uri=https://legit.evil@legit` | userinfo vs host split |
| `redirect_uri=https://legit.evil` subdomain swap | suffix match missed |
| `redirect_uri=https://legit/../@evil` | path normalization |
| `tenant=` enumeration | a built-in tenant returns its own URL — the tenant list is the map |

Expected: the flow redirects the viewer (bot) to a URI you control or into a
tenant you did not provision — the code or token lands in your collector.
Falsifier: redirect_uri is matched strictly against a registered list on every
shape, or the init endpoint ignores the tenant field.

## The flow questions that find the gap

- Who *creates* the identity the SSO step assumes? (race it)
- What does the init endpoint return, and is `redirect_uri` in it? (own it)
- Does token exchange re-verify `redirect_uri`, or only `code`? (swap it)
- Is `state` bound to the session? (CSRF on the callback)

## Falsifier

Registration is gated on existing identity, redirect_uri is strict-matched,
`state` is bound, and the token step re-checks the URI — the flow is closed.

## Traps

- The bot runs on a schedule: plant the pre-created account or the redirect
  state first, then poll for the artifact.
- A `redirect` field in a JSON response is a bigger surface than a 302 — the
  client-side follow may not re-validate the origin.
