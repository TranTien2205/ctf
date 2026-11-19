# PKCE — the code-verifier binding

PKCE (Proof Key for Code Exchange, RFC 7636) binds the authorization code
exchange to the same client that started the flow. Without it, a stolen code
is exchangeable by anyone who has the `client_secret` — or by anyone at all
for a public client.

## How PKCE works

```
Client generates:  code_verifier = random(43-128 chars, URL-safe)
                   code_challenge = BASE64URL(SHA256(code_verifier))
                   code_challenge_method = S256

Authorize request: ...&code_challenge=CHALLENGE&code_challenge_method=S256

Token request:     grant_type=authorization_code&code=CODE&
                   code_verifier=VERIFIER

IdP checks:        SHA256(code_verifier) == code_challenge (from authorize)
```

The `code_verifier` never leaves the client until the token exchange. A code
intercepted in the callback is useless without it.

## The attack shapes

| Shape | The test |
|---|---|
| PKCE not required | start a flow without `code_challenge` — accepted? |
| `code_challenge_method=plain` | the verifier is sent in the clear — equivalent to no PKCE |
| `code_verifier` not re-validated | the token request accepts any verifier |
| `code_challenge` not bound to `client_id` | a challenge from one flow validates a code from another |
| PKCE optional | a confidential client can skip it |

## The probe chain

```bash
# 1. start a flow WITHOUT code_challenge — does the IdP accept it?
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
# if it 302s to the consent page, PKCE is not required

# 2. start a flow with code_challenge_method=plain
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&code_challenge=PLAINTEXT&code_challenge_method=plain"
# if accepted, the verifier is sent in the clear

# 3. exchange a code with a wrong code_verifier
curl -i -X POST "https://idp/token" \
  -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback&code_verifier=WRONG"
# if it returns a token, the verifier is not re-validated
```

## The PKCE-downgrade attack

A client registered for `authorization_code` + PKCE is coerced into a flow
without `code_challenge`. If the IdP accepts it, the client is effectively
not using PKCE — a stolen code is exchangeable by anyone.

```bash
# coerce the client into a no-PKCE flow
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
# the IdP accepts it; the code is now unbound
```

## The `plain` downgrade

`code_challenge_method=plain` sends the `code_verifier` in the clear in the
authorize request — equivalent to no PKCE. The verifier is in the URL, in
the browser history, in the `Referer` of subresource requests.

```bash
# check whether plain is accepted
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&code_challenge=VERIFIER&code_challenge_method=plain"
```

## Falsifier

`code_challenge` is required, `code_challenge_method` is `S256` (not
`plain`), and the token endpoint re-validates `code_verifier` against the
stored challenge. When this holds, the code is bound to the client that
started the flow — move to token binding or account linking.
