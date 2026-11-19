# OAuth/OIDC discovery documents — case catalogue

.well-known/openid-configuration and jwks.json map the auth stack — endpoints, algorithms, keys.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.well-known/openid-configuration | full OIDC map | all endpoints |
| 2 | /jwks.json with key set | public keys | alg confusion check |
| 3 | issuer/registration endpoints | dynamic registration | client-registration attacks |

## Falsifier

Falsifier — no discovery doc or it's minimal: the auth surface isn't self-describing.
