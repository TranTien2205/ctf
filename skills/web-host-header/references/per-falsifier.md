# Per-falsifier — the falsifier for every host-header claim

The falsifier map — a claim, a check that would disprove it.

---

## 1. canonical-URL injection

- **claim**: a reflected host → the app's links point to attacker.com.
- **falsifier**: no host canary reached the body — the canonical URL is built
  from a fixed config value, not the request. `curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'` returns nothing.
- **would reopen**: a canary that reaches a `Location`, `Set-Cookie`, or `<link>`/`<script src>` — a decision-bearing sink.

## 2. reset-link poisoning

- **claim**: a reflected forwarded header → the reset link points to attacker.com.
- **falsifier**: no forwarded canary reached the body or the reset flow — the
  reset link is built from a fixed config value.
- **would reopen**: a canary that reaches the reset link — `curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'` returns it.

## 3. Location redirect

- **claim**: a reflected host → the Location points to attacker.com.
- **falsifier**: no host canary reached the `Location` header — the redirect is
  built from a fixed config value.
- **would reopen**: a canary that reaches the `Location` — `curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'` returns it.

## 4. Set-Cookie fixation

- **claim**: a reflected host → the cookie domain binds to attacker.com.
- **falsifier**: no host canary reached the `Set-Cookie` header — the cookie
  domain is built from a fixed config value.
- **would reopen**: a canary that reaches the `Set-Cookie` — `curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'` returns it.

## 5. cache-poisoning feed

- **claim**: a reflected host → the cache stores the page under attacker.com.
- **falsifier**: no host canary reached the body AND no cache indicator
  (`X-Cache`, `X-Served`, `Age`) changed — the cache does not key on the host.
- **would reopen**: a canary that reaches the body AND a cache indicator that
  changed — `curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'` returns it.

## 6. rewrite ACL bypass

- **claim**: a middleware rewrite → a rewritten path reaches a gated route.
- **falsifier**: no rewrite header reached a gated route — `curl -i -H 'X-Original-URL: /admin' "$BASE/"` returns a 403/404.
- **would reopen**: a rewrite header that reaches a gated route — a 200 with
  the admin body.

## 7. forwarded RFC 7239

- **claim**: a reflected forwarded header → the app's links point to attacker.com.
- **falsifier**: no forwarded canary reached the body — `curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'` returns nothing.
- **would reopen**: a canary that reaches a `Location`, `Set-Cookie`, or `<link>`/`<script src>`.

## 8. duplicated Host

- **claim**: a duplicated Host → the proxy reads the first; the app reads the
  second → a parsing differential.
- **falsifier**: both orders return the same result — no differential.
- **would reopen**: an order that returns a different result — `curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"` vs the reverse.

## 9. malformed Host

- **claim**: a malformed Host → a parsing edge → a differential.
- **falsifier**: the malformed Host returns a 400 — the app rejects it.
- **would reopen**: a malformed Host that returns a different result — `curl -s -D - -H 'Host: evil.example:80' "$BASE/"` vs a clean one.

## 10. absolute-URI

- **claim**: an absolute-URI Host → the proxy reads the Host header; the app
  reads the absolute-URI → a differential.
- **falsifier**: the absolute-URI returns the same result as a clean Host.
- **would reopen**: an absolute-URI that returns a different result — `curl -s -D - "$BASE/" --request-target 'http://evil.example/'` vs a clean one.

## 11. multi-header

- **claim**: a multi-header bypass — a combined injection → a privileged route.
- **falsifier**: the combined injection returns a 403 — no privileged route.
- **would reopen**: a combined injection that returns a 200 — `curl "$BASE/api/internal" -H 'Host: evil.example' -H 'X-Internal: true'` returns it.

## 12. multi-proxy

- **claim**: a multi-proxy chain — a header each strips differently.
- **falsifier**: the header reaches the origin unchanged — no differential.
- **would reopen**: a header that reaches the origin differently — `curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'` returns a different result than a clean one.
