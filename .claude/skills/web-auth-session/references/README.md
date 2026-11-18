# web-auth-session — reference index

The order to read them in; every file exists. ~40 files, ~10k lines.

---

## Routing order

1. **`detection.md`** — map the mechanism, classify the token, pick the file.
2. **`workflow.md`** — the bounded end-to-end loop.
3. **`workflows-deep.md`** — the command-level JWT/session/reset/registration
   ladders.
4. **`ctf-shapes.md`** — the archetype → file table (start here in CTF).
5. **`attack-tree.md`** — the ordered decision map, every branch falsifiable.
6. **`jwt-deep.md`** — JWT attack surface (alg confusion, kid/jku, weak keys).
7. **`jwt-attacks.md`** — the compact JWT field summary.
8. **`extended-jwt.md`** — the extended JWT corpus (confusion variants,
   header injections, claim manipulations).
9. **`claim-payloads.md`** — the forge dictionary (role/admin/identity/flags/
   expiry/aud/iss/amr — ~1800 lines of claim variants).
10. **`verification-surface.md`** — where the verify call lives, what reaches it.
11. **`session-analysis.md`** — opaque ids: entropy, lifecycle, stores.
12. **`session-mgmt-deep.md`** — session lifecycle depth (fixation, rotation,
    concurrent, invalidation).
13. **`cookie-flags.md`** — attribute-level surface (`Secure`, `SameSite`…).
14. **`session-fixation.md`** — fixation + hijacking primitives.
15. **`token-lifecycle.md`** — issue → refresh → expire → revoke.
16. **`password-reset.md`** — reset-token generation, binding, leakage.
17. **`mfa-bypass.md`** — TOTP/OTP/backup-codes/remember-device.
18. **`oauth-flow-issues.md`** — authorize/callback/token/SAML.
19. **`registration-abuse.md`** — register/update/invite/impersonate.
20. **`impersonation.md`** — `/su`, `/switch_user`, `?become=`, masquerade.
21. **`authz-boundaries.md`** — vertical/horizontal/field-level checks.
22. **`api-auth.md`** — bearer/API-key/HMAC/service-token surface.
23. **`framework-auth.md`** — Flask/Django/Express/Rails/Laravel/.NET/Spring/
    Go/PHP per-stack defaults and the greps.
24. **`deep-parsers.md`** — parser differentials: path/header/body/carrier/
    algorithm pinning, field-name variants, number coercion.
25. **`second-order.md`** — the deferred-trust surface.
26. **`second-order-deep.md`** — stored claims, queued sessions, webhooks,
    bot triggers, subdomain fixation.
27. **`account-takeover-chains.md`** — the reusable ATO chains.
28. **`solved-patterns.md`** — the solved-shape catalog (precondition → probe
    → forge → evidence).
29. **`flag-locations.md`** — where the flag lives after the boundary breaks.
30. **`payload-dictionary.md`** — ~350 categorized bodies/headers/claims.
31. **`wordlists.md`** — secrets, ids, endpoint seeds, claim names.
32. **`whitebox-hunt.md`** — the greps for each framework's verify call.
33. **`evidence-rules.md`** — surface/class/impact verdict ladder.
34. **`denied-conditions.md`** — the falsifiers that close each route.
35. **`common-mistakes.md`** — 30 failure modes.
36. **`failed-attempts.md`** — the anti-patterns and why each fails.
37. **`error-analysis.md`** — reading 4xx/5xx to route the next probe.
38. **`cheatsheet.md`** — the 60-second card.
39. **`tooling.md`** — verified `session_dissect`/`jwt_forge`/`http_probe` usage.
40. **`ctf-walkthroughs.md`** — challenge-shape → chain walkthroughs.
41. **`edge-cases.md`** — the corners: unsigned-claim, dual-carrier, JWE/JWE
    confusion, crit/zip headers, unicode/case/null collisions, missing-claim
    defaults, claim-injection via issuer, replay-across-env.

## Cross-skill routes

| The bug is really | Open |
|---|---|
| session cookie is a signed blob | `skills/web-deserialization/` (itsdangerous/Fernet) |
| role field in register body | `skills/web-mass-assignment/` |
| `{"id":2}` swap | `skills/web-idor/` |
| redirect_uri → open redirect | `skills/web-open-redirect/` |
| missing `state` → login CSRF | `skills/web-csrf/` |
| cookie `SameSite=None` → CSRF | `skills/web-csrf/` |
| XSS steals `localStorage` token | `skills/web-xss/` |
| login error differs → user enum | `skills/web-user-enum/` |
| reset via `Host` injection | `skills/web-host-header/` |
| `jku` → SSRF | `skills/web-ssrf/` |
| `sub` claim into SQL | `skills/web-sqli/` |
| SAML assertion XML | `skills/web-xxe/` |
| race on limited-attempt counter | `skills/web-race-condition/` |
| OAuth provider confusion | `skills/web-oauth-sso/` |
| logic bug not a token bug | `skills/web-logic-flaw/` |
| `kid`/`jku` into file-read | `skills/file-read-primitives/` |
| GraphQL resolver-level authz | `skills/web-graphql/` |
| WAF vs app path differential | `skills/web-parser-differential/` |
| stored claim → bot renders | `skills/web-xss/` + `web-prototype-pollution/` |
