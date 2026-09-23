# Sattrack — SOLVED (self-solved; official README was on disk)

- Platform: HackTheBox (web), "Sattrack Bug Bounty Invitational", author lordrukie
- Date: 2026-09-22
- Targets supplied: `154.57.164.83:31210` (app, nginx) and `154.57.164.83:31548`
  (Express "Sattrack Issue Tracker" — the admin bot at `/report`)
- Given credentials: `partner@rockyou.xyz:partn3r123` (never needed)
- Flag: redacted; read live from `/admin/users` with the stolen admin cookie
- Prior attempt in this tree (`challenges/sattrack/solve.py`) had the chain right
  but collected nothing. Two concrete defects, both fixed here.

## Chain

1. **Prototype pollution.** `/login` ships an inline script with a `mergeObjects()`
   deep merge that walks `for (let key in source)` with no `__proto__` guard.
   `JSON.parse` creates `__proto__` as a normal own enumerable property, so the
   merge writes straight onto `Object.prototype`:
   ```json
   {"text":"Invalid email or password",
    "__proto__":{"JS_FILES":["<same-origin script url>","/static/js/login.js"]}}
   ```
2. **Pollution beats the config fetch.** `loadScripts()` runs *after* the merge and
   reads `window.settings.JS_FILES ? window.settings : await retrieveSettings()`.
   `settings` is `{}`, so the polluted prototype supplies `JS_FILES` and the real
   `/api/config` is never consulted. Every entry becomes `<script src>`.
3. **CSP bypass.** CSP is
   `default-src 'self'; script-src 'self' 'unsafe-inline'; ...; connect-src *`,
   so the script src must be same-origin. `/partner/share` (no auth) reflects the
   `type` parameter into a JSON body, so
   `type="}<js>//` closes the object literal and the remainder parses as JavaScript:
   ```
   GET /partner/share?type=%22%7D<js>%2F%2F&data=%22%7Dx
   -> {""}<js>//": "\"}x"}
   ```
   It is served as `Content-Type: text/plain`, but **no `X-Content-Type-Options`
   header is set**, so Chrome still executes it as a script.
4. **Exfil.** The script runs in the admin bot on the app origin; cookies are not
   HttpOnly. `document.cookie` yields the admin JWT
   (`"email":"admin@sattrack.htb","role":"admin"`). The flag is in the admin area
   under `/admin/users` — not `/admin` itself.

## The two defects in the earlier attempt

### 1. `message` must be encoded TWICE

The page decodes it twice and only the second decode is obvious:

```js
const userMessage = params.get('message');          // URLSearchParams already decodes
const userConfig = JSON.parse(decodeURIComponent(userMessage));   // decodes again
```

With a single encode the JSON survives the first decode, but the second one eats
the **share URL's own** percent-encoding inside it. Its `&` then becomes a real
query separator, truncating `type` mid-payload, and its `+` would decode to a
space. Nothing throws — `loadScripts()` just appends a script whose body is not
the payload, and the page looks completely normal. Encoding the whole `message`
twice makes the second decode land exactly on the raw JSON.

### 2. Exfil must be `fetch`, never an image

The CSP declares **no `img-src`**, so `img-src` inherits `default-src 'self'` and
an offsite `new Image().src = ...` is dropped silently. `connect-src` is `*`, so
`fetch()` is the only channel that leaves the origin. The earlier script used
`new Image()` and therefore collected nothing even on the runs where the XSS did
fire.

## Rehearsal is what found both

The payload was run first in a local headless Chrome against the **public** app
origin (`--origin http://154.57.164.83:31210`) instead of `http://127.0.0.1`.
The first rehearsal produced no callback at all, which isolated defect 1 without
spending a bot cycle; the second rehearsal returned
`{"tag":"page","path":"/admin/","body":"{\"error\":\"Token is missing\"}"}` —
proving the XSS and the exfil channel worked end to end and that only the admin
cookie was missing. Only then was the bot fired, and it returned the JWT on the
first try.

## Traps

- The bot's URL filter is `^http:\/\/127\.0\.0\.1\/.*$`, printed verbatim by
  `/report` when it rejects a URL. It is observed, not guessed — submit a bad URL
  once and read the regex out of the error.
- `/admin` and `/admin/` are a dashboard with no flag. The flag sits at
  `/admin/users`. Enumerate the nav `href`s rather than assuming the index page.
- Two ports are supplied and the order is not fixed. Tell them apart by content:
  the report host answers with "Issue Tracker", the app with "Satellite Monitoring
  System" and an nginx `Server` header.
- Keep `/static/js/login.js` in the polluted `JS_FILES` array. Dropping it changes
  page behaviour for no benefit.

## Reusable lessons

- **Count the decodes, not the encodes.** `URLSearchParams.get()` already
  percent-decodes; any further `decodeURIComponent()` is a second decode, and a
  nested URL carried inside that value needs one extra encoding layer per decode
  or its `&` and `+` are destroyed. The failure is silent.
- **Read the CSP for what it omits.** A missing `img-src` is a real restriction
  because it inherits `default-src`, while `connect-src *` is an open door. The
  directive that is absent decided this challenge more than the ones present.
- **`text/plain` still executes as a script when `nosniff` is absent.** Check for
  `X-Content-Type-Options` before dismissing a reflecting endpoint as unusable for
  a CSP `'self'` bypass.
- **Rehearse against the public origin before spending a bot cycle.** The same
  payload with the origin swapped runs in a local headless Chrome and tells you
  whether the XSS fires and whether the exfil channel is open — the only thing it
  cannot supply is the victim's cookie.
