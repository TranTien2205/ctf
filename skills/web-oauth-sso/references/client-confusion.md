# Client confusion — the multi-client surface

When the IdP serves more than one client, the code and token are bound to a
specific `client_id`. Confusion between clients is the surface where a code
minted for one app works on another.

## The registered clients

An IdP typically has a registry: `client_id` → `client_secret`,
`redirect_uris`, `grant_types`, `scopes`, `response_types`, `token_endpoint_auth_method`.
The surface is the gap between what one client is allowed and what another
can do with the same artifacts.

| Check | The test |
|---|---|
| second client registered | enumerate `client_id` values — sequential? predictable? |
| `client_secret` entropy | a second client with a weak or leaked secret |
| `redirect_uri` per client | a code minted for client A's URI works on client B's |
| `grant_type` per client | client A uses `authorization_code`, client B uses `implicit` |
| `scope` per client | client B's token carries a broader scope |
| `token_endpoint_auth_method` | `client_secret_basic` vs `client_secret_post` vs `none` vs `private_key_jwt` |

## The code cross-client exchange

A code minted for `client_id=A` is presented to the token endpoint by
`client_id=B`. The IdP should reject it — the code is bound to the issuing
client. When it does not:

```bash
# mint a code for client A
curl -i "https://idp/authorize?client_id=A&redirect_uri=https://appA/callback&response_type=code&state=XYZ"
# ... user authenticates, code=ABC is delivered to appA

# exchange it as client B
curl -i -X POST "https://idp/token" \
  -d "grant_type=authorization_code&code=ABC&client_id=B&client_secret=SECRET_B&redirect_uri=https://appB/callback"
# if it returns a token, the code is not bound to client_id
```

## The `aud` confusion

The `id_token`'s `aud` claim names the client the token is for. When the app
does not verify `aud`, an `id_token` minted for client A is accepted by client
B — the identity is confused.

```bash
# decode the id_token, check the aud claim
python3 -c "import base64,json; t=open('id_token.txt').read().strip(); print(json.loads(base64.urlsafe_b64decode(t.split('.')[1]+'==')))"
# if aud is a list or a different client_id, the token is not bound to this app
```

## The scope confusion

Client A requests `scope=openid` and gets `openid`. Client B requests
`scope=openid admin` and gets `openid admin`. When the scope check is per-token
rather than per-request, a token minted for client B's broader scope works on
client A's endpoints.

## The implicit/code confusion

Client A uses `authorization_code` (the code is exchanged server-side). Client
B uses `implicit` (the token is in the fragment). When the IdP does not
validate `response_type` per client, a client registered for `code` can be
coerced into `implicit` — the token leaks to the fragment.

```bash
# coerce client A (code-registered) into implicit
curl -i "https://idp/authorize?client_id=A&redirect_uri=https://appA/callback&response_type=token&state=XYZ&nonce=N"
# if it 302s to https://appA/callback#access_token=..., the response_type is not validated
```

## The public/confidential confusion

A `token_endpoint_auth_method` of `none` means the client is public — no
`client_secret`. A code minted for a public client is exchangeable by anyone
who has it (which is why PKCE exists). A confidential client's code requires
the `client_secret`. Confusing the two: a code minted for a confidential
client presented to a public-client token endpoint, or vice versa.

## Falsifier

The code is bound to `client_id`, the `aud` claim is verified, `response_type`
is validated per client, and `token_endpoint_auth_method` is enforced. When
this holds, the client-confusion surface closes — move to state or redirect_uri.
