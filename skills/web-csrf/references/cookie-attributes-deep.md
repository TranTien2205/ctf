# Cookie attributes deep — beyond SameSite

`SameSite` gets the attention, but the full attribute set decides
whether a cookie sets, attaches, and survives. The CSRF-relevant
attributes and their interplay.

---

## 1. The full Set-Cookie anatomy

```text
Set-Cookie: name=value; SameSite=Lax; Secure; HttpOnly; Path=/;
            Domain=.target.com; Max-Age=3600; Expires=...;
            Partitioned; Priority=High
```

| Attribute | CSRF relevance |
|---|---|
| `SameSite` | cross-site attach — the primary gate |
| `Secure` | https-only; required for `SameSite=None`; blocks http delivery |
| `HttpOnly` | JS can't read it — irrelevant to CSRF attach, matters for token-read |
| `Path` | which paths get the cookie — a narrow path misses the write's path |
| `Domain` | which hosts get it — a `.parent.com` cookie reaches subdomains |
| `Max-Age`/`Expires` | persistence — a session cookie dies with the browser |
| `Partitioned` (CHIPS) | partitioned per top-site — a cross-site cookie gets a separate jar |
| `Priority` | eviction order — a low-priority cookie drops under cookie-bombing |

## 2. The `Secure` interplay

```text
SameSite=None REQUIRES Secure — a `SameSite=None` without Secure
is rejected → the cookie never sets → the page can't even get a
session to attack.

Secure on an http-ONLY endpoint → the cookie can't set over http —
the endpoint must be https to get the credential.

a Secure cookie can't be SET from an http page — the cookie-plant
shape needs https.
```

## 3. `HttpOnly` — the read-vs-attach distinction

```text
HttpOnly blocks JS from READING the cookie — but the browser still
ATTACHES it to requests (that's the point of HttpOnly: credentials
attach without being script-readable).

for CSRF: HttpOnly is IRRELEVANT to the attach — the cookie rides
the request whether or not JS can read it. it only matters when you
need to READ the cookie's value (a double-submit cookie you must
echo — HttpOnly blocks that read).
```

The common confusion: HttpOnly does NOT prevent CSRF — it prevents
cookie-THEFT. A CSRF needs the cookie attached, not read.

## 4. `Path` — the cookie's scope

```text
Set-Cookie: session=x; Path=/admin
→ the cookie only attaches to /admin/* requests — a CSRF to
  /api/x gets NO cookie.

a Path=/ cookie attaches everywhere; a Path=/admin cookie misses
/api, /transfer, etc.

the CSRF-write's path must be under the cookie's Path.
```

## 5. `Domain` — the host scope

```text
Set-Cookie: session=x; Domain=.target.com
→ attaches to target.com AND *.target.com — a CSRF from any
  subdomain context.

Set-Cookie: session=x (no Domain)
→ host-only — attaches only to the exact host.

a Domain=.target.com cookie is readable/settable by a subdomain —
a subdomain-XSS or a subdomain-cookie-plant reaches it.
```

## 6. `Partitioned` (CHIPS) — the new isolation

```text
Set-Cookie: session=x; Partitioned; Secure; SameSite=None
→ a partitioned cookie gets a SEPARATE jar per top-level site —
  a cross-site request under a different top-site gets a DIFFERENT
  partition — the victim's cookie doesn't attach from your page.

CHIPS kills the third-party-cookie CSRF surface — a partitioned
cookie is only sent in its own partition context. an embedded/iframe
request under your top-site gets an empty partition.
```

## 7. `Max-Age`/`Expires` — the persistence question

```text
a session cookie (no Max-Age/Expires) dies when the browser closes —
a short-lived bot's jar may hold it only within one session.

a persistent cookie survives — for the shared-jar SSOS shape, the
cookie must persist across bot cycles → it needs an Expires/Max-Age,
or the bot's jar must be a persistent profile (not a fresh context).
```

## 8. `Priority` + cookie-bombing — evicting the real cookie

```text
a cookie-bomb: set many large cookies on the parent domain → the
jar overflows → the browser evicts by Priority (Low first) — the
victim's session cookie gets evicted, then YOUR planted cookie
takes its place.
```

The double-submit bypass pairs this: evict the server's csrf cookie,
plant yours, match the form.

## 9. The `__Host-`/`__Secure-` prefix rules

```text
__Host-  — requires Secure, Path=/, no Domain — a strict cookie
__Secure- — requires Secure

a __Host- session cookie is host-scoped + secure — a subdomain
can't set/overwrite it → the cookie-plant fails on a __Host- cookie.
```

## 10. The "the Set-Cookie itself can be CSRF'd" shape

```text
a login endpoint's Set-Cookie lands in the browser — a cross-origin
POST to it causes the browser to STORE the response's cookie. the
SSOS card's mechanism: the CSRF'd login's Set-Cookie overwrote the
shared jar's token.
```

The response's Set-Cookie processes regardless of the request's
origin — the cookie-write is the primitive, not the request's auth.

## 11. The cookie-jar-persistence probe

```bash
# is the bot's jar persistent across visits?
# visit 1: a page that sets a marker cookie
# visit 2: a page that reads it (or a same-origin endpoint that echoes)
# the SSOS card's jar persisted → the swap held across cycles
```

## 12. The attribute→bypass table

| Attribute | The bypass/block |
|---|---|
| SameSite=Strict | dead — a different credential must carry |
| SameSite=Lax | GET-write top-nav only |
| SameSite=None+Secure | open — all carriers |
| Secure | https page/https target needed |
| HttpOnly | irrelevant to attach; blocks cookie-value read |
| Path=/narrow | the write's path must be under it |
| Domain=.parent | subdomain-settable; subdomain-XSS reaches |
| Partitioned | kills third-party attach — dead for cross-site |
| Max-Age/Expires | persistence — needed for shared-jar |
| __Host- | can't be subdomain-set — blocks the plant |
| Priority=Low | evictable — cookie-bomb |

## 13. The falsifier

```text
a Partitioned or __Host- SameSite=Strict session cookie — the only
credential — with no alternate channel and no same-site write path.
the cookie neither attaches cross-site nor is settable by a
subdomain. class closed for this credential.
```
