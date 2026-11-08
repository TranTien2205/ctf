# Proxy header abuse: hop-by-hop and trust headers

When a front proxy (Traefik, nginx, HAProxy, Envoy) adds or strips headers, two
header lists exist: what the client sent and what the backend believes. Both
directions of that gap are exploitable.

## Naming a proxy-added header in `Connection`

`Connection` is a hop-by-hop header: every value it carries must be removed by
the next hop. Listing a *proxy-added* header there makes the proxy strip its
own injection before the backend sees it.

**Probe pair** (NovaCore, twice on live targets):

```text
GET /api/internal              # authenticated-only endpoint
GET /api/internal
    Connection: X-Real-IP      # name the header the proxy adds
```

Expected: the second arm is accepted without a token — the backend's "came from
the proxy" check (presence of `X-Real-IP`) fails because the proxy dutifully
removed the header the client named. Falsifier: both arms are rejected, so the
trust check does not depend on that header.

The same strip trick works on any hop-by-hop consumer: naming `Authorization`,
`Cookie`, or a WAF-decision header in `Connection` can drop it before a layer
that needed it — or drop a *client-supplied* spoofed header before a layer that
would have rejected it.

## Injecting the trust header directly

The inverse: the backend trusts a header the proxy normally owns, and the proxy
forwards client-supplied copies untouched.

```text
GET /admin-only
    X-Forwarded-For: 127.0.0.1
GET /admin-only
    X-Real-IP: 127.0.0.1
```

Try the full trust-header family: `X-Forwarded-For`, `X-Real-IP`,
`X-Forwarded-Host`, `X-Original-URL`, `X-Rewrite-URL`, `Forwarded`. A header the
proxy appends to (rather than replaces) leaks the injection as a second list
element — `127.0.0.1, real.ip` — which some backends still trust.

## Falsifier

Both arms behave identically: either the proxy sanitizes the header properly,
or the backend never trusted it. Compare the *body* — a 200 on both arms can
hide that one arm reached the internal handler.

## Traps

- Pick the endpoint out of source or recon first; a 404 on both arms means the
  path is wrong, not the technique (recorded trap on NovaCore).
- Some proxies only strip `Connection`-named headers on specific versions or
  when the value matches exactly; retry with the literal casing the proxy used.
