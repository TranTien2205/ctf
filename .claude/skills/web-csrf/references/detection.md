# Detection — finding the CSRF-able endpoint

CSRF needs three things in one place: a state-changing endpoint, a
credential the browser attaches automatically, and no request value
the attacker page can't read. The detection pass hunts each one.

---

## 1. The endpoint inventory

```bash
# every state-changing route — POST/PUT/PATCH/DELETE + write-y GETs
grep -rnoE 'app\.(post|put|patch|delete)\s*\(|router\.(post|put|patch|delete)|@(app|route)\.(post|put|patch|delete)|@app\.route\([^)]*methods=\[[^]]*POST|methods=["'"'"']POST|def\s+(post|put|patch|delete)|\.handle\(|http\.HandleFunc|gin\..*\.(POST|PUT|PATCH|DELETE)|mux\.HandleFunc' \
  <src> --include='*.js' --include='*.ts' --include='*.py' \
  --include='*.go' --include='*.rb' | grep -v node_modules | head -80
```

The CSRF candidate is a route that CHANGES state — writes, updates,
deletes, transfers, follows, votes, settings, profile, password,
email, role, invite, purchase, transfer, withdraw, connect, submit,
approve, enable, disable, add, remove, delete, create, update,
change, reset, revoke, grant, assign, bind, link, unlink, join,
leave, invite, share, publish, upload, import, apply, configure,
register, enroll, subscribe, unsubscribe, redeem, claim, exchange,
swap, move, copy, rename, reorder, sort, flag, mark, note, tag,
comment, rate, review, report, block, mute, follow, unfollow,
friend, unfriend, like, unlike, star, unstar, watch, unwatch, pin,
unpin, bookmark, favorite, save, archive, restore, trash, purge.

## 2. The credential check — what the browser attaches

```bash
# cookies — the usual carrier
Set-Cookie: session=...; [SameSite=?] [Secure] [HttpOnly]
Set-Cookie: token=...;  [SameSite=?] [Secure] [HttpOnly]
# NTLM/Kerberos — auto-auth
WWW-Authenticate: NTLM / Negotiate
# client certs — auto-presented
# HTTP Basic/Digest — browser attaches
Authorization: Basic / Digest
```

CSRF requires an AMBIENT credential — one the browser attaches
without JS. `Authorization: Bearer` in a JS-set header is NOT
ambient — it's the anti-CSRF pattern (the attacker page can't read
the token to set the header). Cookies, NTLM, client certs, and
Basic/Digest are ambient.

## 3. The SameSite audit — the cookie's attach rule

```bash
# the attach matrix
SameSite=Strict   → cookie sent ONLY same-site — CSRF dead for it
SameSite=Lax      → sent on top-level GET navigations + same-site —
                    a GET write ships; a POST doesn't
SameSite=None     → sent everywhere — but requires Secure
(no attribute)    → default is Lax in modern Chrome/Edge/Firefox
```

The `SameSite` attribute on the AUTH cookie decides whether the
browser attaches it cross-site at all. `SameSite=None` (with Secure)
or a MISSING attribute (pre-2020 default) or a GET-reachable write
on `SameSite=Lax` are the open shapes.

## 4. The gate inventory — what COULD block it

For each candidate endpoint, what stops a cross-origin request?

| Gate | The check | Bypass |
|---|---|---|
| CSRF token | a session-bound value in the body/header | weak/ungated/misbound tokens — `token-defenses.md` |
| Origin/Referer check | the server reads a header the browser sets | header-check gaps — `origin-referer.md` |
| Content-Type gate | `application/json` required — a form can't send it | `text/plain` JSON / parser leniency — `content-type-gate.md` |
| Custom header required | `X-Requested-With`/`X-CSRF` — a form can't set headers | CORS open (different class); form can't do it — falsifier |
| SameSite=Strict | cookie not attached | GET-write on Lax; no bypass on Strict |
| Bearer-token auth | the token isn't ambient | falsifier — not CSRF-able |
| re-auth/password confirm | an interactive check | some apps skip on APIs |

## 5. The "is the endpoint reachable by a form" test

```bash
# a form POST — same-origin first to confirm it parses
curl -i -X POST "$BASE/change" -d 'name=csrf-marker' -b "$COOKIE_JAR"
# then the content-type gate
curl -i -X POST "$BASE/change" -H 'Content-Type: text/plain' \
  -d '{"name":"csrf-marker"}' -b "$COOKIE_JAR"
curl -i -X POST "$BASE/change" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'name=csrf-marker' -b "$COOKIE_JAR"
```

`csrf_probe.py --url --method POST --body 'name=x'` replays three
ways: as-sent, `--token-field` stripped, foreign-origin — grading
each.

## 6. The bot surface — the CTF delivery target

```bash
# a /report, /visit, /submit-url, /check, /preview endpoint
grep -rnoE '(report|visit|submit-url|submit_url|check-url|preview|render|browse|crawl|screenshot|admin-bot|headless|puppeteer|playwright|selenium|chromedriver)' \
  <src> --include='*.js' --include='*.py' | grep -v node_modules | head -40
```

A bot that visits a supplied URL while holding a privileged session
is the CSRF delivery vehicle — the write fires under the bot's
ambient credentials inside its browser context.

## 7. The "the write is already reachable directly" falsifier

```bash
curl -i -X POST "$BASE/change" -d 'name=csrf-marker' -b "$COOKIE_JAR"
# if YOUR direct request with YOUR credentials succeeds — the write
# is just an IDOR/mass-assignment/authz issue, not CSRF. CSRF is
# the delivery shape when YOUR context can't reach the write but
# the VIEWER's can.
```

CSRF is the right class when the write needs the VIEWER's ambient
credential — a privileged bot's session, a localhost socket-peer,
a cookie you don't have. If your own credentials already reach it,
the bug is elsewhere (authz/IDOR/mass-assignment).

## 8. The detection checklist

```text
[ ] state-changing route exists (writes, not reads)
[ ] credential is ambient (cookie/NTLM/cert, not Bearer)
[ ] SameSite on the auth cookie: Strict/Lax/None/missing?
[ ] the write's method: GET (Lax-ok) vs POST (needs None/missing)
[ ] the gate inventory: token? Origin? Content-Type? custom-header?
[ ] each gate's enforcement: verified, or just present?
[ ] a delivery target: a bot, an admin viewer, or self-CSRF?
[ ] the read-back oracle: where the state change becomes visible
```

## 9. The ledger

```bash
python3 tools/state.py <chal> --hypothesis "csrf: POST /change reachable via text/plain form, SameSite missing"
```
