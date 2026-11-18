# Fetcher fingerprint — reading the callback's request

The callback's raw request is the fetcher-dissected — its source-ip,
UA, headers, body, timing — the whole fetch-context read off one
hit.

---

## 1. The hit-record — what the listener captures

```text
oob_listener records: method / path / headers / body / source-ip /
   timestamp — the full inbound-request — the fetcher reveals
   itself:
{
  "method": "GET",
  "path": "/canary-tag",
  "headers": {"User-Agent": "libcurl/7.81.0", "Accept": "*/*",
              "X-Forwarded-For": "…"},
  "body": "",
  "source_ip": "10.0.0.5",
  "ts": "..."
}
every field is a signal — read them all
```

## 2. The User-Agent — the fetcher's name

```text
the UA names the client-lib → the scheme-list + the behavior:
  libcurl/7.x / curl/7.x     → libcurl — the scheme-rich — gopher
                                file dict ldap ftp — the money
  python-requests/2.x         → requests — http(s) only — parser-
                                diff only
  Python-urllib/3.x           → urllib — http+file+ftp — file-read!
  Java/11 / Java/17           → java-url — jar netdoc file
  okhttp/4.x                  → android-http — http-only
  Go-http-client/1.1 / 2.0    → golang — http-only
  GuzzleHttp/7 / Guzzle/6     → php-guzzle — http
  WordPress/6.x               → wp-http — http — gopher-stripped
  Symfony HttpClient/Curl     → php — curl-backed → gopher!
  node-fetch / undici / axios → node — http(s)+ws
  faraday / Ruby / httparty   → ruby — http(s)
  Apache-HttpClient/4.x       → java-apache — http
  Dalvik/x                    → android — http
  Mozilla/5.0 (X11; Linux x86_64) Headless Chrome → a BROWSER —
                                the bot-visit class — different —
                                the payload is html+js — the
                                fetch is a browser-navigation —
                                xss-adjacent
  no-User-Agent               → a raw-socket or a lib that doesn't
                                set one — requests-with-no-ua —
                                or the app strips it
```

## 3. The source-ip — the fetcher's position

```text
the source-ip is the egress-ip — the fetcher's network-position:
  - a public-cloud-ip → a cloud-vm — the metadata-IP reachable
  - a private-ip → the fetcher is inside the target-net — the
    internal-position — the fetcher's OWN network is yours to map
  - a proxy-ip → the fetch went through an egress-proxy — the
    proxy is the real fetcher — the proxy's position differs —
    the proxy may have its own scheme-cap
  - 127.0.0.1 → the fetcher shares your host? unusual — usually
    means the "fetch" was local — or the listener is on the box
the source-ip is ALSO the fetcher's egress — an internal-answer
from a DIFFERENT host than the web → the deferred-fetch's worker
```

## 4. The headers — what the app sends

```text
the headers are intel — the app's outbound-headers:
  - Accept / Accept-Encoding — the fetcher's accept-set
  - X-Forwarded-For — does the app FORWARD your ip? — the app's
    own outbound-xff — the forward-behavior
  - Authorization / X-Api-Key / Cookie — the app forwards CREDENTIALS
    cross-origin? — the token-leak — the forwarded-auth — if your
    listener got an Authorization header → the app leaks creds —
    that token may work on internal-services
  - Referer — the referer the app sends
  - custom-app-headers — X-Internal-*, X-App-* — internal-tokens
  - the webhook-signature — a signing-secret — forge-ability
  - Host: your-host — the host-header the fetcher sets — the vhost
```

## 5. The body — the request-payload

```text
a POST-fetcher's body — the app may send a body — the webhook-
payload — the event-data — the app's outbound-data — sometimes
secrets — the payload's shape — the body is the app's template —
its secrets/keys may ride
```

## 6. The timing — when it fired

```text
the hit-timestamp → the schedule:
  - immediate → synchronous — the request-response is the channel
  - +seconds → a fast-queue — the worker polls quickly
  - +minutes → a cron — the tick
  - +hours → a batch — the deferred-shape — webhook-deferred.md
  - the EVENT-driven timing — fires right after your action —
    the action is the trigger — the event-map
```

## 7. The path — the url-shape the fetcher kept

```text
the hit's path — what survived of your url:
  - /canary-tag → the url-path rode — normal
  - /?x=y → the query rode
  - the path-shape reveals the url-construction — appended-paths?
    query-mangled?
  - a truncated-path → the url was cut at a char — the boundary-
    finding — where the url-parse stopped
```

## 8. The second-hit — the follow-behavior

```text
did it hit you TWICE? — the fetcher re-fetches — retries — or the
redirect-follow — your 302-answer → the second-hit is the follow —
the redirect-follow is the family-opener — the chain exists
did it hit you with a DIFFERENT shape? — the OPTIONS-then-GET —
the HEAD-then-GET — the method-progression
```

## 9. The "which-fetcher" decision-table

```text
UA                       → fetcher    → schemes            → first-chain
libcurl/curl/*           → libcurl     → all incl gopher    → file→gopher
python-requests/*        → requests    → http(s)            → internal-http
Python-urllib/*          → urllib      → http+file+ftp      → file:///flag
Java/*                   → java        → http+jar+netdoc+file→ netdoc/file
Go-http-client/*         → golang      → http(s)            → internal-http
GuzzleHttp/*             → php-guzzle  → http(s)            → internal-http
Symfony HttpClient/Curl  → php+curl    → curl-schemes       → file→gopher
node-fetch/undici/axios  → node        → http(s)+ws         → internal+ws
faraday/Ruby/HTTParty    → ruby        → http(s)            → internal+open()-trick
WordPress/*              → wp          → http(s)            → internal-http
okhttp/*                 → android     → http(s)            → internal-http
Headless-Chrome          → browser     → different-class    → xss-adjacent
```

## 10. The "no-callback" — the silent-case read

```text
no hit → the absence is data:
  - egress-blocked → the internal-probe decides — egress-blocked.md
  - the param isn't fetched → the display-shape — not-ssrf
  - the deferred-queue → later — the schedule — wait or trigger
  - the fetch-failed — dns/parse — the canary-host didn't resolve —
    the dns-side — try a literal-ip canary? — your listener's ip —
    bypasses dns — http://1.2.3.4:9000/ — the ip-canary — dns
    was the failure not the fetch
the ip-canary is the dns-independent probe — a raw-ip url needs
no resolution — the fetcher's dial reaches you — the dns-failure
was the variable
```

## 11. The multi-fetcher — the two-context split

```text
the url-param may go to TWO fetchers — the immediate-fetch AND a
deferred-one — the immediate is curl (gopher-ok) — the deferred is
a browser (xss) — the SAME param, two contexts — the canary-
hits show two different UAs — the two-context param — each gets
its own chain
```

## 12. The header-forward test — the auth-leak

```text
the critical observation: does the callback carry an auth/cookie/
api-key header? — the app forwards creds cross-origin — the
leaked-token:
  - use the token on internal-services — the internal-auth-bypass
  - the token IS the app's internal-credential — the worker/admin
    services accept it
the callback that carries a secret-header → the cross-origin-leak
→ the token is the escalation — the internal-auth is yours
```
