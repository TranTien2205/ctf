# Glossary — the parser-differential vocabulary

The terms the corpus uses — each with its definition.

---

## The core terms

```text
parser-differential     a front-end and a back-end parse the request
                        differently — a header's trust, a path's
                        normalization, a client-supplied header — the
                        disagreement is the vulnerability.
hop-by-hop              a header that controls only one hop — a proxy
                        strips it before forwarding — a Connection
                        header's names.
hop-by-hop bypass       naming the proxy's own header in Connection —
                        the proxy strips it — the app sees a request
                        without the trusted header — a missing-header
                        fallback treats it as local — the trust check
                        bypassed.
client-supplied         a proxy header the client supplies — the app
                        trusts it without verifying the proxy added it.
missing-header fallback the app's behavior when a trusted proxy header
                        is absent — a local request, a skipped check.
trust check             the app's check that reads the proxy's header —
                        a local-vs-remote check, an internal-route check,
                        an admin check.
local request           a request the app treats as originating on the
                        proxy's host — a trusted request.
internal route          a route gated to internal traffic — an internal
                        check.
gated route             a route gated by a check — an authenticated-only,
                        an internal, a restricted.
restricted endpoint     a route gated by a restriction — a token_required,
                        an internal, an admin.
authenticated-only      a route gated by an authentication check — a
                        token_required, a login_required.
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
proxy header            a header a proxy adds — an X-Real-IP, an
                        X-Forwarded-*, a CF-*, an X-Amzn-*.
client-supplied header  a proxy header the client supplies — the app
                        trusts it without verification.
trusted header          a proxy header the app trusts — the check's input.
```

## The header terms

```text
X-Real-IP               a proxy's client-IP header — the real client IP.
X-Forwarded-For         a proxy's forwarded-IP header — the client IP
                        chain.
X-Forwarded-Host        a proxy's forwarded-host header — the original
                        Host.
X-Forwarded-Proto       a proxy's forwarded-proto header — the original
                        scheme.
X-Forwarded-Scheme      a proxy's forwarded-scheme header — the original
                        scheme.
X-Forwarded-User        a proxy's forwarded-user header — the authenticated
                        user.
X-Forwarded-Email       a proxy's forwarded-email header — the authenticated
                        email.
X-Forwarded-Server      a proxy's forwarded-server header — the original
                        server.
X-Client-IP             a proxy's client-IP header — the client IP.
True-Client-IP          a proxy's true-client-IP header — the client IP
                        (Akamai).
Forwarded               the RFC 7239 forwarded header — the client IP,
                        host, scheme.
X-Original-URL          a proxy's original-URL header — the original path.
X-Rewrite-URL           a proxy's rewrite-URL header — the rewritten path.
X-Forwarded-Prefix      a proxy's forwarded-prefix header — the original
                        prefix.
X-Forwarded-Path        a proxy's forwarded-path header — the original
                        path.
X-Original-Path         a proxy's original-path header — the original path.
X-Real-Path             a proxy's real-path header — the real path.
X-Internal              a proxy's internal header — an internal-route flag.
X-Admin                 a proxy's admin header — an admin flag.
X-Debug                 a proxy's debug header — a debug flag.
X-HTTP-Method-Override  a proxy's method-override header — a method
                        rewrite.
X-Original-Method       a proxy's original-method header — a method
                        rewrite.
X-HTTP-Method           a proxy's method header — a method rewrite.
X-Method-Override       a proxy's method-override header — a method
                        rewrite.
```

## The mechanism terms

```text
normalization           a path the front-end and the back-end normalize
                        differently — a traversal, an encoding, a case
                        difference — a route-confusion.
normalization differential  a path the front-end normalizes one way and
                        the back-end another — the front-end's check
                        reads a different path than the app's.
route-confusion         a path the front-end's check gates but the back-
                        end's route reaches — a gated route reached
                        through the differential.
desync                  a front-end and a back-end that parse the request
                        boundary differently — a request-smuggling.
store                   a stored copy that serves YOUR input — a cache-
                        poisoning.
parse                   a front-end and a back-end that parse the request
                        differently — a parser-differential.
read                    a fetch that reads bytes — a cors.
session                 a trust check that reads a session / a token —
                        an auth-session.
host check              a trust check that reads a Host header — a host-
                        header.
fetch                   a server-side fetch — an ssrf.
```

## The proof terms

```text
differential confirm    a two-request check — a normal request then a
                        stripped request — a 200 on the gated route →
                        the differential confirmed.
bypass evidence         the response bytes — a 200 on the gated route —
                        the check bypassed — the route reached.
readback                the downstream's effect read back — the response
                        carries the route's output.
falsifier               a condition that kills the differential — a
                        proxy that doesn't strip, a proxy that strips
                        the client header, a proxy that verifies, a non-
                        header check, the same parse.
```

## The budget terms

```text
mechanism budget        5 probes or 15 minutes per mechanism class.
challenge budget        25 probes or 45 minutes for the whole challenge.
escalation              the spent-budget strategy — chain_match →
                        reclassify → writeup_search → novel_plan →
                        fanout_sweep → solver_handoff → stop_report.
```
