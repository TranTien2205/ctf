# Glossary — the host-header vocabulary

The terms the corpus uses — each with its definition.

---

## The core terms

```text
host-header             a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key, a middleware rewrite — the app's
                        trust check reads the host's value.
canonical URL           the app's generated links — a reflected host
                        poisons the links — the links/scripts point to
                        attacker.com — a stored injection.
password-reset link     a reset link built from a forwarded header — a
                        reflected forwarded header poisons the link —
                        the link points to attacker.com — an account
                        takeover.
Location redirect       a redirect built from the Host header — a
                        reflected host poisons the redirect — the
                        Location points to attacker.com — an open
                        redirect.
Set-Cookie domain       a cookie bound to the Host header — a reflected
                        host poisons the domain — the cookie binds to
                        attacker.com — a session fixation.
cache key               a cache that stores pages under the Host header
                        — a reflected host poisons the cache key — the
                        cache stores the page under attacker.com — a
                        cache-poisoning feed.
middleware rewrite      a middleware that reads a rewrite header for
                        the path — a rewritten path reaches a gated
                        route — an ACL bypass, a route-confusion, an
                        internal route reached.
```

## The header terms

```text
Host                    the canonical Host header — the app's generated
                        links, reset links, redirects, cookie domains,
                        cache keys.
X-Forwarded-Host        a forwarded host header — the app's generated
                        links, reset links, redirects.
X-Host                  a forwarded host header — the app's generated
                        links, reset links, redirects.
X-Forwarded-Server      a forwarded server header — the app's generated
                        links, reset links, redirects.
X-HTTP-Host-Override    a forwarded host header — the app's generated
                        links, reset links, redirects.
X-Forwarded-Proto       a forwarded proto header — the app's generated
                        links, redirects.
X-Forwarded-Scheme      a forwarded scheme header — the app's generated
                        links, redirects.
X-Forwarded-Port        a forwarded port header — the app's generated
                        links, redirects.
X-Forwarded-Path        a forwarded path header — the app's generated
                        links, rewrites.
X-Forwarded-Prefix      a forwarded prefix header — the app's generated
                        links, rewrites.
X-Forwarded-User        a forwarded user header — the app's generated
                        links, user checks.
X-Forwarded-Email       a forwarded email header — the app's generated
                        links, user checks.
X-Forwarded-For         a forwarded IP header — the app's local-vs-remote
                        checks.
Forwarded               the RFC 7239 forwarded header — the app's
                        generated links, checks.
X-Original-URL          a rewrite header — the middleware's path rewrite.
X-Rewrite-URL           a rewrite header — the middleware's path rewrite.
X-Original-Path         a rewrite header — the middleware's path rewrite.
X-Real-Path             a rewrite header — the middleware's path rewrite.
```

## The proxy terms

```text
proxy                   a front-end that forwards requests to a back-end —
                        an nginx, a Traefik, an Apache, an HAProxy, a
                        Cloudflare, a CloudFront, an Akamai, a Varnish, a
                        Squid.
reverse proxy           a proxy that forwards to a back-end — the front-
                        end layer.
forward proxy           a proxy that forwards to an external host — the
                        egress layer.
edge                    the outermost proxy — a CDN, a Cloudflare, a
                        CloudFront, an Akamai.
origin                  the innermost proxy — the app's own proxy.
gateway                 a proxy that adds an application-layer policy —
                        a WAF, an API gateway.
WAF                     a web application firewall — a proxy that filters
                        requests.
```

## The mechanism terms

```text
parsing differential    a byte or a structure the proxy and the app
                        parse differently — a duplicated Host, a
                        malformed Host, an absolute-URI Host.
duplicated Host         a duplicated Host — the proxy reads the first;
                        the app reads the second → a differential.
malformed Host          a malformed Host — a trailing dot, a double-
                        dot, an @-separator, a #-separator, a ?-
                        separator, an empty host, a forged port → a
                        parsing edge → a differential.
absolute-URI Host       an absolute-URI Host — a request-line
                        differential — the proxy reads the Host header;
                        the app reads the absolute-URI → a differential.
rewrite                 a middleware that reads a rewrite header for
                        the path — a rewritten path reaches a gated
                        route — an ACL bypass.
route-confusion         a path the proxy's check gates but the back-
                        end's route reaches — a gated route reached
                        through the differential.
ACL bypass              an access-control check bypassed — a gated
                        route reached through the rewrite.
```

## The proof terms

```text
reflected host          a reflected host in the response is only a
                        lead — the finding needs the host reaching a
                        decision.
host reaching a decision a host reaching a decision — a link the
                        victim clicks, a path the middleware applies, a
                        domain a cookie binds to.
bypass evidence         the response bytes — a 200 on the gated route —
                        the check bypassed — the route reached.
readback                the downstream's effect read back — the response
                        carries the route's output.
falsifier               a condition that kills the differential — a
                        proxy that validates, a proxy that strips, a
                        proxy that verifies, a non-header check, the
                        same parse.
```

## The budget terms

```text
mechanism budget        5 probes or 15 minutes per mechanism class.
challenge budget        25 probes or 45 minutes for the whole challenge.
escalation              the spent-budget strategy — chain_match →
                        reclassify → writeup_search → novel_plan →
                        fanout_sweep → solver_handoff → stop_report.
```
