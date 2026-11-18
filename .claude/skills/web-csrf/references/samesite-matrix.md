# The SameSite matrix — when the browser attaches the cookie

`SameSite` decides whether the auth cookie rides a cross-site
request at all. The whole class hinges on this one attribute —
and on the browser version's default for a missing attribute.

---

## 1. The three values + the missing case

| Attribute | Cross-site attach rule |
|---|---|
| `SameSite=Strict` | NEVER sent cross-site — CSRF dead for this cookie |
| `SameSite=Lax` | sent on TOP-LEVEL GET navigations only — a GET write ships; POST/PUT/DELETE/fetch/img don't get it |
| `SameSite=None` | sent on every request — requires `Secure` |
| no attribute | browser-dependent default — modern Chrome/Edge/Firefox = Lax; older = None-equivalent |

The CTF-critical cases: `SameSite=None` (explicit open), a MISSING
attribute on an older browser (default lax-equivalent-to-None), and
the GET-write-on-Lax edge (a state change reachable by GET is a
CSRF under Lax).

## 2. The GET-write-on-Lax shape — the most-missed case

```text
Set-Cookie: session=abc; SameSite=Lax
GET /transfer?to=attacker&amount=1   → the browser attaches the
                                       cookie — a top-level nav is
                                       'same-site-ish' under Lax
```

`Lax` blocks POST/fetch/img cross-site but ALLOWS top-level GET
navigations — a link click, a form GET, a `window.open`, a
`<meta http-equiv=refresh>`, an `<iframe>` top-level nav. If the
state change is a GET (search-params write, a GET-with-side-effect),
Lax doesn't protect it.

## 3. The delivery shapes per SameSite value

```text
SameSite=Strict
  form GET top-level nav      → cookie NOT sent
  form POST top-level nav     → cookie NOT sent
  <img>/<script>/<iframe> GET → cookie NOT sent
  fetch/xhr                   → cookie NOT sent
  websocket                   → cookie NOT sent
  → DEAD for the Strict cookie — a different credential must carry
    (a second cookie without Strict? a non-cookie auth?)

SameSite=Lax
  form GET top-level nav      → cookie SENT — the open case
  <a href> click              → SENT — a top-level nav
  form POST top-level nav     → NOT sent
  <img>/<script>/<iframe> GET → NOT sent (sub-resource, not nav)
  fetch/xhr                   → NOT sent
  websocket                   → NOT sent
  window.open/location GET    → SENT — top-level nav
  <meta refresh>              → SENT — a navigation
  → only a GET-reachable write, via a top-level navigation

SameSite=None + Secure
  everything                  → cookie SENT — full CSRF surface

no attribute (modern browser)
  → treated as Lax — GET-nav only

no attribute (pre-2020 browser / a bot's old chromium)
  → treated as None — everything sent
```

## 4. The bot's browser — the real SameSite environment

A CTF bot's headless Chrome/puppeteer/playwright may run a browser
old enough or flagged to attach differently:

```text
- Chromium ≥80 defaults missing-SameSite to Lax
- a bot launched with --disable-features=SameSiteByDefaultCookies
  attaches like None — a launch flag the challenge ships
- a bot on an older chromium (≤79) attaches like None
- a puppeteer/playwright default may differ from Chrome
```

White-box check: `grep -rn 'SameSite\|disable-features' <src>` for
the bot's launch flags — `--disable-features=SameSiteByDefaultCookies`
is a deliberate SameSite-off flag some challenges set to make the
bot CSRF-able.

## 5. The `SameSite=None` requires `Secure` rule

```text
Set-Cookie: x=1; SameSite=None           → REJECTED by modern browsers
                                           — None REQUIRES Secure
Set-Cookie: x=1; SameSite=None; Secure   → accepted, sent everywhere
```

A `SameSite=None` WITHOUT `Secure` is silently rejected — the cookie
never sets — a subtle challenge shape: the cookie LOOKS open but
never lands. Conversely `SameSite=None; Secure` needs the page to
be HTTPS to set.

## 6. The cookie-attribute audit command

```bash
# what does the auth cookie look like?
curl -i "$BASE/" | grep -i 'set-cookie'
curl -i "$BASE/login" -d 'u=x&p=y' | grep -i 'set-cookie'
# the answer decides the whole class:
#   SameSite=Strict → not CSRF via this cookie
#   SameSite=Lax    → GET-write only, top-level nav only
#   SameSite=None;Secure → full surface
#   missing         → modern=Lax, old-bot=None-equivalent
```

## 7. The "Lax + a GET write" carrier set

```html
<!-- a top-level GET navigation — Lax attaches the cookie -->
<a href="https://target/transfer?to=me&amount=1">x</a>
<form method="GET" action="https://target/transfer">
  <input name="to" value="me"><input name="amount" value="1">
</form>
<script>location='https://target/transfer?to=me&amount=1'</script>
<script>window.open('https://target/transfer?to=me&amount=1')</script>
<meta http-equiv="refresh" content="0;url=https://target/transfer?to=me&amount=1">
<!-- all five are top-level navigations — Lax attaches -->
```

The `<img src>` shape does NOT work under Lax — a sub-resource GET
is not a top-level navigation. The common mistake.

## 8. The POST-via-Lax edge cases

```text
- a POST form that re-navigates top-level: the POST itself doesn't
  attach (it's a POST), but the RESPONSE's redirect is a GET-nav —
  a two-step shape: POST (no cookie) → 302 → GET (cookie attached).
  Useless unless the write is GET-reachable anyway.

- a same-site-redirect chain: attacker.com → target.com/redirect?u=
  attacker-page → the second nav IS a top-level nav on target —
  but the redirect lands on target's own page — useless for a POST.

- the 'Lax+POST' draft behavior (old): a missing-SameSite cookie
  got a 2-minute Lax+POST window on Chrome ~80-85 — a freshly-set
  cookie attached to cross-site POSTs within 2 min of being set.
  Dead on modern; a history note only.
```

## 9. When the bot's browser predates Lax-default

```text
Chrome ≤79, the bot's headless build, or a --disable-features flag
→ a missing-SameSite cookie attaches like None — the full CSRF
surface opens even without SameSite=None
```

This is THE reason CTF CSRF works so often — the bot's browser is
configured lax, or the challenge predates the default. Check the
bot's UA/launch config when source exists.

## 10. The matrix → which write-shape survives

| Cookie | GET write (top-nav) | POST write (form) | fetch/ws write |
|---|---|---|---|
| Strict | no | no | no |
| Lax | YES | no | no |
| None+Secure | yes | YES | YES |
| missing, modern | YES | no | no |
| missing, old bot | yes | YES | YES |

The write's METHOD is the decision — a POST endpoint under Lax
needs the cookie to be `None` or missing-on-old-bot.

## 11. The falsifier

```text
SameSite=Strict on the only credential AND no alternate credential
channel — the cookie never attaches cross-site; every delivery
fails. Record refutes.
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "samesite: cookie is Lax; write must be GET-reachable top-nav"
```
