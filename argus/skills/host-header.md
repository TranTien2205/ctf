# Host-header attacks & middleware ACL bypass

**When:** the app (or its middleware/proxy) trusts request headers to build
absolute URLs, resolve the vhost, or route internally. Signals:
`X-Forwarded-Host` reflected in links/`Location`, a 403 on an admin path
that middleware might rewrite to, password-reset links containing the
attacker's host.

`probe_xfh` sends a canary `X-Forwarded-Host` and reports where it lands;
with `restricted` it also tests the X-Original-URL/X-Rewrite-URL bypass.

## First probes

1. `X-Forwarded-Host: canary.invalid` - reflected into body/Location?
   Reflected host in generated links = reset-poisoning material: request a
   password reset for your own account, check whether the emailed URL uses
   the injected host.
2. Header ladder beyond XFH: `X-Host`, `X-Forwarded-Server`,
   `X-Forwarded-For`, `Forwarded:`, duplicate `Host:` headers, absolute-URI
   in the request line.
3. With a restricted path known (`/admin`, `/internal`): send it via
   `X-Original-URL`, `X-Rewrite-URL`, `X-Override-URL`, `X-Original-URL`
   on a BENIGN outer request. Middleware (nginx rewrite, IIS, some Rails
   stacks) routes on the header while the edge ACL checked the outer path.

## Confirmation

- XFH reflected: the canary appears verbatim in a link/`Location` served
  to a request without the header too (cache poisoning) or at least in
  the direct response (poisoning lead).
- ACL bypass: the restricted path 401/403s on direct access but returns
  its content under `X-Original-URL`/`X-Rewrite-URL`. Quote the differing
  body bytes from both requests.

## Bypasses

- `X-Forwarded-Host` stripped -> `X-Host`, `Forwarded:`, `Host:` twice,
  `Host: victim.com:80` port tricks, trailing-dot `victim.com.`.
- Absolute-form request target (`GET http://evil/ HTTP/1.1`) with a legal
  `Host:` - some frontends route on the request line.
- Header ACL bypass variants: `X-Original-URL`, `X-Rewrite-URL`,
  `X-Override-URL`, `X-Forwarded-Prefix`, plus path encodings the edge
  does not normalize (`/%61dmin`, `/admin;.css`).

## Falsifier

Canary never reflects, and restricted-path headers return the same body
as the outer request - middleware ignores them or the edge normalizes
before routing.

## Severity guide

Reflected host used in password-reset links: medium-high (account
takeover via poisoning). ACL bypass to an admin surface: high. Bare
reflection with no generated-link use: informational.
