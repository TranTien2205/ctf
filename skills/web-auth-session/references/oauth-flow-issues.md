# OAuth / SSO Flow Issues

## Common OAuth 2.0 Roles to Identify
```
Resource Owner  → the user
Client          → the application requesting access (target app)
Authorization Server → issues tokens (e.g. Google, Okta, custom IdP)
Resource Server → hosts protected resources
```

## State Parameter (CSRF Protection)
```
[ ] Is "state" parameter present in the authorization request?
[ ] Is it validated on callback (matches what was sent)?
[ ] Is it tied to the user's session, or is it static/predictable?

Test: remove or reuse an old "state" value on the callback URL and see if
the flow still completes — indicates missing CSRF protection on the OAuth
flow, allowing login CSRF or account linking attacks.
```

## Redirect URI Validation
```
[ ] Does the authorization server validate redirect_uri strictly (exact
    match) or loosely (prefix match, wildcard, any subdomain)?

Test variations:
https://target.com/callback          (legitimate)
https://target.com/callback/../evil  (path traversal)
https://target.com.attacker.com/callback   (subdomain confusion)
https://target.com@attacker.com/callback   (userinfo confusion)
https://target.com%2f@attacker.com/callback

If a loosely-validated redirect_uri is accepted, authorization codes/tokens
can be exfiltrated to attacker-controlled endpoints.
```

## Authorization Code Interception
```
[ ] Is PKCE (Proof Key for Code Exchange) used? If not, and the client is
    public (mobile/SPA), authorization code interception is easier.
[ ] Is the authorization code single-use and short-lived?
[ ] Is the code bound to the redirect_uri used in the initial request?
```

## Token Leakage via Referer
```
[ ] After redirect back to the client with token/code in URL, does the
    page load any third-party resources (analytics, ads, fonts)? If so,
    the Referer header may leak the token/code to that third party.
```

## Account Linking / Confusion
```
[ ] If the app allows login via multiple providers (Google, Facebook,
    email), does it link accounts based on unverified email claims?
[ ] Can an attacker register with the target email at a less-trusted
    provider (self-hosted OIDC, etc.) and log in as the victim if the
    app trusts the email claim without verification?
```

## Implicit Flow Risks (Legacy, Should Be Deprecated)
```
[ ] Is the implicit flow (response_type=token) still supported?
[ ] Does it expose the access token directly in the URL fragment,
    increasing exposure via browser history, logs, Referer?
```

## Scope Escalation
```
[ ] Can the "scope" parameter be modified by the client to request
    broader permissions than intended, if the authorization server doesn't
    enforce a maximum per-client scope?
```

## Testing Checklist Summary
```
[ ] state parameter present, validated, session-bound
[ ] redirect_uri validated with exact match, no open redirect
[ ] PKCE used for public clients
[ ] authorization code single-use, short expiry, bound to redirect_uri
[ ] no token/code leakage via Referer to third-party resources
[ ] account linking verifies email ownership, doesn't trust unverified claims
[ ] scope parameter cannot be escalated beyond client's registered scopes
```
