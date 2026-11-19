# Edge cases — the OAuth shapes that do not fit the model

The OAuth model assumes a clean authorization-code flow. The edge cases are
the flows that deviate — the device flow, the client-credentials flow, the
resource-owner-password flow, the hybrid flow, the non-standard IdP.

## The device flow

The device flow (RFC 8628) is for devices that cannot run a browser: the
device polls the token endpoint with a `device_code` while the user
authenticates on a separate device. The attack surface: the `device_code` is
a bearer artifact — whoever polls first gets the token.

```bash
# the device polls the token endpoint
curl -i -X POST "https://idp/token" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=DC&client_id=APP"
# the IdP returns a token once the user has authenticated on the other device
# the attacker polls faster — the token lands on the attacker's client
```

## The client-credentials flow

`grant_type=client_credentials` — the client exchanges its `client_id` +
`client_secret` for a token directly. No user, no redirect, no code. The
attack surface: a leaked `client_secret` is a direct token mint.

```bash
# mint a token with client credentials
curl -i -X POST "https://idp/token" \
  -d "grant_type=client_credentials&client_id=APP&client_secret=SECRET&scope=openid"
```

## The resource-owner-password flow

`grant_type=password` — the user gives the client their username and password;
the client exchanges them for a token. The attack surface: the client sees
the user's credentials — a phishing surface, and a credential-harvesting
client can mint tokens directly.

```bash
# the client exchanges the user's credentials for a token
curl -i -X POST "https://idp/token" \
  -d "grant_type=password&username=victim&password=secret&client_id=APP&client_secret=SECRET"
```

## The hybrid flow

`response_type=code id_token` or `code token` — the callback carries both a
code and a token. The token is in the fragment (the implicit leak), the code
is in the query (the replay surface). Both surfaces are live at once.

## The `form_post` response mode

`response_mode=form_post` delivers the code/token in a POST body instead of
the URL. The POST body is not in the URL — no history, no Referer leak — but
it is in the response body, readable by a same-origin script.

## The `web_message` response mode

`response_mode=web_message` delivers the code/token via `postMessage` to a
named frame. The `postMessage` target is the attack surface — if the target
origin is not validated, the code is delivered to a different frame.

## The non-standard IdP

A custom IdP that does not follow the RFC exactly: a `state` that is not
echoed back, a `redirect_uri` that is validated against a stored list but
not the request's, a `code` that is not bound to `client_id`. The audit
walks the flow once and names each deviation.

## The multi-tenant IdP

A shared IdP serving multiple applications. The `aud` claim names which app
the token is for; when `aud` is not verified, a token minted for app A works
on app B. The cross-client surface is the multi-tenant surface.

## The `login_hint` injection

`login_hint=victim@domain` prefills the IdP's login form. When the hint is
reflected into the page without encoding, it is a DOM injection — a `state`
that is reflected is a `state` that can inject.

## The `id_token_hint` replay

`id_token_hint` is a previous `id_token` used to hint the identity. When the
IdP accepts an `id_token_hint` without verifying it, a captured token is
replayable.

## The `request`/`request_uri` parameter

`request` is a JWT carrying the whole authorize request (JAR, RFC 9101).
`request_uri` is a URL the IdP fetches the request from. Both are surfaces:
the JWT's signature may not be verified, and the URI may be SSRF-able.

## The backchannel logout

Backchannel logout (OIDC) sends a `logout_token` to the client's backchannel
endpoint. The `logout_token` is a JWT — its signature and claims are the
attack surface.
