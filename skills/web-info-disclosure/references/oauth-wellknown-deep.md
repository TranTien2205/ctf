# OAuth/OIDC discovery documents — deep

.well-known/openid-configuration and jwks.json map the auth stack — endpoints, algorithms, keys.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no discovery doc or it's minimal: the auth surface isn't self-describing.

## Highest-cost traps

- The discovery doc is the OIDC attack map — capture the endpoint list.
- RS256→HS256 confusion uses the jwks key as HMAC secret — auth class's exploit.
- Registration endpoints sometimes accept arbitrary redirect_uris.

## Commands

```bash
curl -s '$BASE/.well-known/openid-configuration'
```

## Cross-references

`api-docs-exposure.md` · `../web-auth-session/`
