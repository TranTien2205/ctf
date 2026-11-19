# Authorization code flow — the canonical OAuth attack surface

The authorization code flow is the one you see most: the user is redirected to the
identity provider, authenticates, and is redirected back to the application with a
`code` in the URL. The application exchanges the code for an access token
server-side. Every step is a potential attack surface.

## The flow, step by step

```
User ──► GET /login ──► 302 Location: https://idp/authorize?
                          client_id=APP&redirect_uri=https://app/callback&
                          response_type=code&state=XYZ&scope=openid

User ──► (authenticates at the IdP)

IdP  ──► 302 Location: https://app/callback?code=ABC&state=XYZ

App  ──► POST /token  {grant_type=authorization_code, code=ABC,
                        client_id=APP, client_secret=SECRET,
                        redirect_uri=https://app/callback}

IdP  ──► {access_token: AT, id_token: JWT, refresh_token: RT}

App  ──► GET /userinfo (Authorization: Bearer AT) ──► session established
```

## Where the attack surface lives

| Step | Parameter / artifact | What goes wrong |
|---|---|---|
| authorize | `redirect_uri` | not an exact match — prefix, subdomain, or open-redirect chain |
| authorize | `state` | not bound to the session, so a flow started by the attacker completes for the victim |
| authorize | `scope` | the app accepts a scope it did not request, or the IdP grants more |
| callback | `code` | not bound to the client — replayed against a different client |
| callback | `code` | leaked via Referer, logs, or the back button |
| token | `client_secret` | leaked in source, JS, or the token request is over plain HTTP |
| token | `redirect_uri` | not validated on exchange — the code is used against a different URI |
| userinfo | `access_token` | bearer token in URL, logged, or replayed cross-client |

## The first discriminating probe

Walk the whole flow once with the browser jar open, recording every redirect,
parameter, and cookie set before changing any of them. The transcript is the
exploit surface: the cookie swap, the state mismatch, the redirect chain all
live in the ordering of writes, not in any single request.

```bash
# capture the full authorize→callback→token→userinfo transcript
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | grep -E "Location:|Set-Cookie:|code=|state=" | tee transcript.txt
```

A `state` that is not cryptographically bound to the session cookie is the
single most common bug: start the flow as the attacker, capture the
`authorize` redirect, have the victim visit it, and the victim's session lands
on the attacker's account — or vice versa, depending on the linking model.

## The state parameter

`state` exists to bind the authorize request to the callback. When it is:

- **Missing** — the app may not validate it at all; test with a stateless
  callback replay.
- **Not bound to the session** — a flow started by the attacker can be
  completed by the victim (the CSRF shape).
- **Predictable** — sequential or timestamp-derived; test with a second flow
  to see the pattern.
- **Reflected into the page** — a DOM sink; an attacker-controlled state can
  inject HTML or JS into the callback page.

The falsifier: `state` is a cryptographically random value stored in the
session cookie before the redirect, and the callback rejects any state that
does not match the session's stored value. When this holds, the CSRF shape
closes — move to redirect_uri or token binding.
