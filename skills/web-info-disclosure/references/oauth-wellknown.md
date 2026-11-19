# OAuth/OIDC discovery documents

.well-known/openid-configuration and jwks.json map the auth stack — endpoints, algorithms, keys.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.well-known/openid-configuration | full OIDC map | all endpoints |
| /jwks.json with key set | public keys | alg confusion check |
| issuer/registration endpoints | dynamic registration | client-registration attacks |

## Steps

1. Fetch /.well-known/openid-configuration and /oauth/.well-known/openid-configuration.
2. The doc names every endpoint: auth, token, userinfo, registration, jwks.
3. jwks.json holds public keys — the alg-confusion check (RS256→HS256) belongs to auth class.
4. Dynamic registration endpoints may allow self-provisioning a client.

## Falsifier

Falsifier — no discovery doc or it's minimal: the auth surface isn't self-describing.

## Traps

- The discovery doc is the OIDC attack map — capture the endpoint list.
- RS256→HS256 confusion uses the jwks key as HMAC secret — auth class's exploit.
- Registration endpoints sometimes accept arbitrary redirect_uris.

## Commands

```bash
curl -s '$BASE/.well-known/openid-configuration'
```

## Cross-references

`api-docs-exposure.md` · `../web-auth-session/`
