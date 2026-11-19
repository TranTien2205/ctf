# Token binding — the code and token trust surface

The authorization code and the access token are both bearer artifacts: whoever
presents them is trusted. The binding question is *who* they are bound to.

## The code binding

The `code` is issued for a specific `client_id` + `redirect_uri` + `user`.
The token exchange should re-validate all three.

| Check | The test |
|---|---|
| code bound to `client_id` | exchange a code minted for client A with client B's credentials |
| code bound to `redirect_uri` | the token request's `redirect_uri` must match the authorize step's exactly |
| code single-use | exchange the same code twice |
| code expiry | capture a code, wait, exchange it |
| code bound to `state`/`nonce` | a code minted with one `state` should not exchange with another |

```bash
# exchange a code twice — the second should fail
curl -i -X POST "$IDP/token" -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback"
curl -i -X POST "$IDP/token" -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback"
# if both return tokens, the code is not single-use

# exchange a code with a different redirect_uri
curl -i -X POST "$IDP/token" -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://evil.com/callback"
# if it succeeds, the code is not bound to redirect_uri
```

## The token binding

The access token is a bearer token — whoever holds it is trusted. The binding
question is *what* it is bound to.

| Check | The test |
|---|---|
| token bound to `client_id` | use client A's token against client B's `userinfo` |
| token bound to `scope` | a token minted for `openid` should not work for `profile` |
| token bound to `user` | a token minted for user A should not read user B's data |
| token expiry | capture a token, wait, use it |
| token audience | a token minted for app A should not work on app B |

## The `id_token` binding

The `id_token` is a JWT carrying the identity claims. The binding question is
whether the app verifies it correctly.

| Check | The test |
|---|---|
| signature verified | strip the signature, or sign with `alg=none` |
| `aud` matches `client_id` | an `id_token` minted for client A should not be accepted by client B |
| `iss` matches the expected IdP | a token from a different IdP should be rejected |
| `exp`/`iat`/`nbf` validated | an expired or not-yet-valid token should be rejected |
| `nonce` matches | a replayed `id_token` should be rejected |

```bash
# decode the id_token
python3 -c "import base64,json; t=open('id_token.txt').read().strip(); p=t.split('.'); print(json.dumps(json.loads(base64.urlsafe_b64decode(p[1]+'==')),indent=2))"

# alg=none — strip the signature
python3 -c "import base64,json; h=json.dumps({'alg':'none','typ':'JWT'}); p=json.dumps({'iss':'https://idp','sub':'victim','aud':'APP','exp':9999999999,'iat':0,'nonce':'N'}); print(base64.urlsafe_b64encode(h.encode()).rstrip(b'=').decode()+'.'+base64.urlsafe_b64encode(p.encode()).rstrip(b'=').decode()+'.')"
```

## The PKCE binding

PKCE binds the code exchange to the same client that started the flow via a
`code_challenge`/`code_verifier` pair. The binding question is whether it is
enforced.

| Check | The test |
|---|---|
| `code_challenge` required | start a flow without `code_challenge` — accepted? |
| `code_challenge_method` | `S256` or `plain` — `plain` sends the verifier in the clear |
| `code_verifier` re-validated | the token request must carry the verifier that hashes to the challenge |

```bash
# start a flow without PKCE
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
# if accepted, PKCE is not enforced — a stolen code is exchangeable by anyone
```

## Falsifier

The code is bound to `client_id` + `redirect_uri` + `state`/`nonce` and is
single-use with a short expiry. The token is bound to `client_id` + `scope` +
`user` + `aud`. The `id_token` signature is verified with an allowlisted
algorithm, `aud`/`iss`/`exp`/`nonce` are validated, and PKCE is required with
`S256`. When this holds, the token surface closes — move to account linking
or the cookie jar.
