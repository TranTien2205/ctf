# Sub-resource vs navigation — the request-context difference that decides SameSite

The single distinction that decides whether `SameSite=Lax` blocks
your delivery: is the request a top-level navigation or a sub-
resource?

---

## 1. The two request contexts

```text
top-level navigation — the browser's main frame loads a new document:
- a link click, a form GET, location=, window.open, a meta-refresh,
  a typed URL
- Sec-Fetch-Mode: navigate, Sec-Fetch-Dest: document

sub-resource — a resource the page embeds:
- <img>, <script>, <link>, <iframe>, <video>, <audio>, <object>,
  <embed>, fetch, xhr, sendBeacon, EventSource
- Sec-Fetch-Mode: no-cors|cors, Sec-Fetch-Dest: image|script|iframe|
  empty|...
```

## 2. Why Lax treats them differently

```text
SameSite=Lax's rule: 'the cookie attaches on a top-level GET nav
because a link-click is a legitimate same-site-ish action — the
user chose to navigate'. a sub-resource is a passive embed — the
attacker page controls it, not the user.
```

`Lax` is the web's compromise: let links/forms work (top-nav), block
passive embeds (sub-resources).

## 3. The GET-on-Lax carrier set — every top-nav

```html
<a href="https://t/x?a=1">x</a>                    <!-- click — user nav -->
<script>location='https://t/x?a=1'</script>        <!-- script nav -->
<meta http-equiv=refresh content="0;url=https://t/x?a=1">  <!-- meta nav -->
<script>window.open('https://t/x?a=1')</script>    <!-- popup — blockable -->
<form action="https://t/x" method=GET>...</form>   <!-- form GET nav -->
```

All `Sec-Fetch-Mode: navigate` — the Lax exception applies.

## 4. The POST-on-Lax reality — a POST is never a safe nav

```text
a top-level POST form IS a navigation (Sec-Fetch-Mode: navigate)
but SameSite=Lax still blocks the cookie — because POST is a 'write'
method, and Lax's exception is ONLY for 'safe' methods (GET/HEAD).
```

A POST form-nav is a navigation BUT the cookie doesn't attach under
Lax — the method matters, not just the nav-ness.

## 5. The Sec-Fetch-Mode/Dest read — the server's own gate

```text
the server can check Sec-Fetch-Mode + Sec-Fetch-Site:
- 'if Mode == navigate and Site == cross-site' → a cross-site nav —
  Lax already attaches here
- 'if Dest == image|script and Site == cross-site' → a sub-resource —
  already cookieless under Lax
```

A `Sec-Fetch-Site: cross-site` check gates BOTH — but the `none`
value (a typed URL, a no-site nav) bypasses a `cross-site`-only check.

## 6. The "a sub-resource CAN'T be a top-nav" — the delivery split

```text
to attach a Lax cookie:
  the request MUST be a top-level GET nav — a form GET, a link, a
  location=, a meta-refresh — NOT an <img>/<script>/<iframe>/fetch
to ship a body (POST):
  the cookie must be None/missing — Lax never attaches to a POST
```

The split: GET-write → top-nav → Lax-safe. POST-write → needs None
cookie or a different credential.

## 7. The iframe-src vs iframe-srcdoc distinction

```html
<iframe src="https://t/x?a=1"></iframe>      <!-- a sub-resource GET —
                                              Dest: iframe — Lax blocks -->
<iframe srcdoc="<form ...>">                   <!-- the srcdoc page is
                                              same-origin — its form is
                                              a same-site nav -->
```

`src` is a sub-resource (cookieless under Lax); `srcdoc` is same-
origin content — its form submits as same-site.

## 8. The redirect-launders-nav — a redirect's context

```text
a top-nav to a URL that 302s to the write — the nav's context is
preserved through the redirect chain (mostly) — the Lax cookie
attaches through the nav even after a redirect, as long as it stays
a top-level GET nav.
```

## 9. The POST-nav-that-becomes-GET — a 302 after POST

```text
a POST form submits (no Lax cookie) → the response 302s → the
browser GETs the Location (a nav — Lax attaches on the second hop).
useless unless the WRITE is on the GET, not the POST.
```

## 10. The falsifier

```text
the write is POST-only AND the cookie is Lax AND no GET-write sibling
AND no None/missing credential — the top-nav exception can't reach
a POST. the class is closed via the cookie; a non-cookie credential
or a stored page is the only vector.
```

## 11. The decision

```text
Lax cookie + GET-write exists    → top-nav GET carrier — open
Lax cookie + POST-write only     → closed via cookie — different credential
None/missing cookie              → any carrier
Strict cookie                    → closed for this credential
```
