# Why CSRF works — the ambient-authority model

CSRF isn't a "bug in the endpoint" — it's a consequence of how
browsers attach credentials. The model that makes the class make
sense.

---

## 1. The ambient-authority principle

```text
a browser attaches credentials to requests AUTOMATICALLY — cookies,
HTTP-auth, client-certs — based on the DESTINATION, not on which
page initiated the request. an attacker page can't read the cookie
(HttpOnly) but can fire a request that carries it.
```

The credential is "ambient" — it rides every request to its domain
regardless of who asked. CSRF is the abuse of that ambient attach.

## 2. The confused-deputy frame

```text
the server is the 'confused deputy': it sees a valid request from
the victim's session and can't tell the victim didn't mean it. the
request is well-formed, authenticated, and indistinguishable from
a legitimate one — because it IS legitimate from the server's view.
```

CSRF defenses all reduce to "distinguish a victim-intended request
from an attacker-fired one": a token only the real page knows, a
SameSite cookie the attacker's page can't attach, an Origin the
attacker can't forge, a content-type a form can't produce.

## 3. Why the four defenses work — and where each gaps

| Defense | Why it works | The gap |
|---|---|---|
| SameSite=Strict | the cookie never attaches cross-site | a non-cookie credential, a same-site context |
| CSRF token | only the real page knows it | the token must be session-bound, verified, unreadable cross-origin |
| Origin/Referer check | the attacker can't set a fake one | absent/null bypass, substring match, a stored page |
| content-type whitelist | a form can't send application/json | a lenient parse accepts text/plain JSON |

Every defense has a gap because every check relies on something the
attacker either can't produce OR can partially control.

## 4. Why `no-cors` sends but doesn't read

```text
the SOP lets a page SEND a request cross-origin (it's how the web
loads cross-site images/scripts/forms) — but can't READ the response
without CORS. CSRF exploits the SEND half: the write fires, the
response is opaque, the state changes.
```

The web's cross-origin send is a feature (hyperlinks, images, forms)
— CSRF is the unintended write-consequence of that feature.

## 5. Why the token works — the capability model

```text
a CSRF token is a CAPABILITY: the real page holds it, the attacker
page can't read it (it's in the page's DOM or a cookie the SOP
blocks). the server checks the capability — a request without it is
assumed attacker-fired.

the token fails when:
- the attacker can READ it (a CORS-open endpoint, a JS-readable
  cookie, a leaked meta tag)
- the token isn't session-bound (a global/static token is a known
  value)
- the check isn't enforced (a token accepted-from-anywhere)
```

## 6. Why SameSite is the modern defense

```text
SameSite moves the check to the BROWSER: 'don't attach this cookie
to a cross-site request'. it's a declaration on the credential
itself — the server trusts the browser to enforce it. stronger than
a token (no server-side check to misimplement) — but only for
cookie-based credentials, and subject to the Lax exception for
top-level GET navs.
```

## 7. Why the GET-write is the persistent hole

```text
SameSite=Lax protects POST but not top-level GET — because GET is
'safe' and a nav to a GET is a legitimate link. an app that mutates
on a GET (a 'delete?id=' link, a transfer-GET) violates the
safe-method assumption — and Lax deliberately lets it through.
```

The GET-write is the hole the web's architecture can't close without
breaking links.

## 8. Why the bot's position is a credential

```text
the TornadoService card: the 'credential' isn't a cookie — it's the
bot's 127.0.0.1 socket position. ambient authority isn't only cookies
— any property the victim's context carries (its IP, its localhost
position, its session, its shared jar) is the ambient credential
the CSRF rides.
```

## 9. The defense-in-depth reality

```text
real defense needs ALL of: SameSite + a token + Origin check +
content-type. each alone has a gap; together they cover each other.
a CTF challenge usually removes one — the skill's job is naming
WHICH gate is open.
```

## 10. The model → the workflow

```text
the ambient-authority model is the workflow:
  1. name the ambient credential (cookie? position? jar?)
  2. name what the browser attaches it to (SameSite decides)
  3. name what distinguishes a real request (token? Origin? ct?)
  4. find the ONE distinguishing check that's missing/broken
  5. fire the request that passes every other check
```
