# Header pairs that reach a sink

The app trusts one or more host-shaping headers when building URLs or when
middleware rewrites the request. Each header is one cheap request — send a
canary, read where it lands.

## The sweep

```bash
for h in "X-Forwarded-Host" "X-Host" "X-Forwarded-Server" "X-HTTP-Host-Override"; do
  curl -s -o /dev/null -D - -H "$h: canary.example" "$BASE/" | grep -i 'location\|set-cookie'
done
curl -s -H 'Forwarded: host=canary.example' "$BASE/" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt"
```

## Sinks, by value

| Sink | Payoff |
|---|---|
| Password-reset link built from the header | account takeover — request a reset for YOUR account, read the delivered link |
| `Location` / redirect target | open redirect, SSO flow poisoning |
| `Set-Cookie: domain=` | session fixation surface |
| Canonical/OG URLs in the body | cache poisoning feed — poison once, the cache serves your host to everyone |
| `X-Original-URL` / `X-Rewrite-URL` | middleware path rewrite — a 403'd path served through the header is an ACL bypass |

## The ACL-bypass shape

```bash
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
```

Front-end frameworks (Next.js middleware, Express routers, edge workers)
match the URL before or after rewrite — whichever side wins decides whether
the header reaches protected routes. Try both headers and both the root path
and a dummy path as the outer URL.

## Traps

- A 400/421 on a foreign Host means the server validates — that header is a
  dead end, move to `X-Forwarded-*` and `Forwarded:` before writing it off.
- Reflection into the body is only a lead; the finding is the header reaching
  a decision a victim depends on.
- Duplicated `Host` headers: some front ends take the first, some the last —
  `Host: good` + `Host: evil` on one request is worth one probe when the
  single-header form is rejected.
