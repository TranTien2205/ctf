# OAuth/OIDC discovery documents — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.well-known/openid-configuration | full OIDC map | all endpoints |
| /jwks.json with key set | public keys | alg confusion check |
| issuer/registration endpoints | dynamic registration | client-registration attacks |

## Falsifier

Falsifier — no discovery doc or it's minimal: the auth surface isn't self-describing.
