# OAuth/OIDC discovery documents — checklist

.well-known/openid-configuration and jwks.json map the auth stack — endpoints, algorithms, keys.

## Checklist

- [ ] Fetch /.well-known/openid-configuration and /oauth/.well-known/openid-configuration.
- [ ] The doc names every endpoint: auth, token, userinfo, registration, jwks.
- [ ] jwks.json holds public keys — the alg-confusion check (RS256→HS256) belongs to auth class.
- [ ] Dynamic registration endpoints may allow self-provisioning a client.

## Abort conditions

- The discovery doc is the OIDC attack map — capture the endpoint list.
- RS256→HS256 confusion uses the jwks key as HMAC secret — auth class's exploit.
- Registration endpoints sometimes accept arbitrary redirect_uris.

## Falsifier

Falsifier — no discovery doc or it's minimal: the auth surface isn't self-describing.
