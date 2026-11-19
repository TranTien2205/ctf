# Class boundary — what is OAuth/SSO vs what is not

The OAuth/SSO class is the delegation-flow surface: the authorize→callback→token→session sequence. The boundary is what is not this class.

## The confusable classes

| Class | The signal | The boundary |
|---|---|---|
| `web-auth-session` | a local login, a session cookie, a JWT | no IdP, no redirect, no code exchange |
| `web-open-redirect` | a redirect parameter that is not validated | the redirect is the bug, not the OAuth flow |
| `web-race-condition` | a race on a check-then-act window | the race is the mechanism, not the OAuth flow |
| `web-csrf` | a cross-site request that is not validated | the CSRF is the bug, not the OAuth flow |
| `web-ssrf` | a server-side fetch of an attacker-controlled URL | the SSRF is the bug, not the OAuth flow |
| `web-prototype-pollution` | a prototype or class pollution reaching a fallback | the pollution is the bug, not the OAuth flow |
| `web-deserialization` | a serialized object trusted without validation | the deserialization is the bug, not the OAuth flow |
| `web-logic-flaw` | a business-logic step that is skipped or reordered | the logic flaw is the bug, not the OAuth flow |

## The boundary rules

1. **OAuth/SSO is the delegation flow.** If there is no IdP, no `authorize`
   endpoint, no `code` exchange, no `redirect_uri` — it is not OAuth/SSO.
   A local login is `web-auth-session`.

2. **The race is the mechanism, not the class.** A registration race that
   delivers a cookie swap is `web-oauth-sso` — the race is how the swap is
   delivered, but the swap is what hijacks the session. A race on a balance
   check or a stock check is `web-race-condition`.

3. **The open redirect is the mechanism, not the class.** An open redirect
   inside the `redirect_uri` path is part of the OAuth flow — the code is
   delivered to the attacker via the redirect chain. A standalone open
   redirect is `web-open-redirect`.

4. **The CSRF is the mechanism, not the class.** A `state` that is not bound
   to the session is an OAuth CSRF — the flow is hijacked, not just a request.
   A CSRF on a non-OAuth endpoint is `web-csrf`.

5. **The cookie swap is the class.** Two cookies in one jar — the app session
   and the IdP token — and a `loginSSO` that ignores credentials is the
   OAuth/SSO surface. A session-fixation or session-hijack without an IdP is
   `web-auth-session`.

6. **The linking is the class.** Account linking on `email` or `username` —
   the OAuth identity mapped to a local account — is the OAuth/SSO surface.
   A mass-assignment or IDOR on the account is `web-logic-flaw` or `web-idor`.

## The reclassification signals

| Observation | Reclassify to |
|---|---|
| no IdP, no redirect, no code — a local login form | `web-auth-session` |
| a redirect parameter that is not validated, no OAuth flow | `web-open-redirect` |
| a race on a balance or stock check, no OAuth flow | `web-race-condition` |
| a CSRF on a non-OAuth endpoint | `web-csrf` |
| a serialized object trusted without validation | `web-deserialization` |
| a prototype pollution reaching a fallback | `web-prototype-pollution` |
| a business-logic step skipped or reordered | `web-logic-flaw` |

## The shared-signal resolution

Some signals appear in multiple classes. The resolution order:

1. Is there an `authorize` endpoint, a `redirect_uri`, a `code`, a `callback`?
   → `web-oauth-sso`
2. Is there a local login form, a session cookie, a JWT?
   → `web-auth-session`
3. Is there a redirect parameter that is not validated, no OAuth flow?
   → `web-open-redirect`
4. Is there a race on a check-then-act window, no OAuth flow?
   → `web-race-condition`
