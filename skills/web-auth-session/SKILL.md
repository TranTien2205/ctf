---
name: web-auth-session
description: >
  Authentication and session management vulnerability testing. Use when
  challenge involves login flows, password reset, session tokens, JWTs,
  MFA, or access control between roles. Supports token analysis, JWT attacks,
  and broken access control detection.
tags: [web, auth, session, jwt, access-control, broken-auth]
environment: [ctf, lab, authorized-testing]
budget:
  max_attempts: 4
  stuck_threshold: 3
  time_hint: "25m"
  on_stuck: pivot
  stop_conditions:
    - "JWT alg confusion fails both variants"
    - "token tamper rejected 3 times"
    - "session fixation not accepted"
---

# Auth & Session CTF Playbook

## Scope & Safety
- Only test with accounts you control or are authorized to use
- Avoid account lockout brute forcing against real user accounts without agreement
- Document exact token/session values used in testing (redact before sharing)

## Login Flow Analysis
```
[ ] Is there rate limiting / account lockout on failed attempts?
[ ] Does error message differ for "user not found" vs "wrong password"
    (username enumeration)?
[ ] Is credential transmitted over HTTPS only, never in URL/GET?
[ ] Is there CSRF protection on the login form?
[ ] Does "remember me" use a separate, long-lived token?
```

## Username Enumeration
```bash
curl -s -d "user=admin&pass=x" https://target.com/login
curl -s -d "user=nonexistent_XYZ&pass=x" https://target.com/login
# Compare response text, status code, timing
```

## Password Reset Flow
```
[ ] Is reset token in URL predictable (sequential, timestamp-based, short)?
[ ] Is reset token single-use and expiring?
[ ] Does the reset confirmation leak the token via Referer header to
    third-party resources (analytics, CDN)?
[ ] Can the "email" field be manipulated to send reset to attacker-controlled
    address (host header injection, parameter pollution)?
```

## Session Token Analysis
```
[ ] Token entropy — is it long/random or short/predictable?
[ ] Token reused across sessions/users?
[ ] Session fixation — can attacker set victim's session ID before login?
[ ] Cookie flags: HttpOnly, Secure, SameSite=Strict/Lax
[ ] Does logout actually invalidate the session server-side?
[ ] Is session tied to IP/User-Agent (session hijacking harder) or not?
```

## JWT Attacks
See `references/jwt-attacks.md` for detailed technique list.
```bash
# Decode JWT header/payload (no verification)
echo "<jwt>" | cut -d. -f1 | base64 -d
echo "<jwt>" | cut -d. -f2 | base64 -d

# Try alg:none attack
python3 -c "
import jwt
print(jwt.encode({'user':'admin'}, key='', algorithm='none'))
"
```

## Access Control / Privilege Escalation
```
[ ] Vertical: can a low-priv user access admin-only endpoints directly?
[ ] Horizontal: can user A access user B's resources (see web-idor)?
[ ] Missing function-level access control: is admin functionality reachable
    by guessing/discovering the URL even without a visible link?
[ ] Role parameter in registration/profile update (mass assignment to admin)?
```

## MFA Bypass Checks
```
[ ] Can MFA step be skipped by directly navigating to post-login URL?
[ ] Is MFA code brute-forceable (no rate limit, short numeric code)?
[ ] Does "remember this device" cookie bypass MFA entirely, and is it
    predictable/reusable across accounts?
[ ] Backup codes predictable or reused?
```

## OAuth/SSO Flow Issues
```
[ ] State parameter present and validated (CSRF in OAuth flow)?
[ ] Redirect URI validation strict or wildcard/open redirect?
[ ] Token leakage via Referer header on redirect to third party?
```

## Decision Tree
- JWT-based session → `references/jwt-attacks.md`
- Predictable/weak session tokens → `references/session-analysis.md`
- Role/privilege confusion → treat as access control finding, cross-check
  with `web-idor` for horizontal access issues
- OAuth/SSO flow → `references/oauth-flow-issues.md`

## Output Required
- Auth mechanism (form-based, JWT, OAuth, session cookie)
- Enumeration/lockout behavior
- Token analysis results (entropy, predictability, algorithm)
- Access control bypass confirmed or denied
- Recommended remediation-relevant finding summary

## References
- `references/jwt-attacks.md` - JWT algorithm confusion, none-alg, key confusion
- `references/session-analysis.md` - Session token entropy and fixation testing
- `references/oauth-flow-issues.md` - OAuth/SSO common misconfigurations
