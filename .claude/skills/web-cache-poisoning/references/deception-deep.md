# Deception deep — the stored-response confusions, exhaustively

Every way a stored response reaches the wrong context — the mechanics.

---

## 1. The authenticated-page-served-anonymously — the verified card

```text
an authenticated page cached under a URL the anonymous requester
also fetches — the cache keys on the URL, not the auth state — the
stored copy is the privileged page served to anyone.
```

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # anonymous — HIT?
#   the anonymous request returns the authenticated page (a 200 with
#   the content, not a 302 to login) → deception
```

```text
the mechanism: the cache doesn't distinguish 'your authenticated
copy' from 'the anonymous requester's copy' — one URL, one stored
response — the auth state isn't in the key.
```

## 2. The personalized-page-served-publicly — the per-user leak

```text
a personalized page (a profile, a dashboard, a session-scoped)
cached under a shared URL — the stored copy serves YOUR personalized
content to every requester — a session-data leak.
```

```text
the mechanism: the cache keys on the URL, not the session — the
stored copy carries YOUR session's content — every requester's copy
has it.
```

## 3. The unkeyed-header-poisoned-page — the injected response

```text
an unkeyed reflected header — YOUR header's effect is stored under
the public URL — every requester's copy carries YOUR injected
content.
```

## 4. The path-normalization deception — the route confusion

```text
a path the cache and the app normalize differently — a static-looking
URL served the dynamic response — the stored copy's URL is the
victim's URL, the response is YOUR request's.
```

```bash
# a path the cache normalizes but the app routes differently
curl "$BASE/static/../admin?cb=<unique>"
#   the cache stores it under /static/../admin; the app serves /admin
```

## 5. The Host-header deception — the URL-rewrite leak

```text
an unkeyed Host/X-Forwarded-Host — the app's absolute URLs use YOUR
host — the stored copy's links point to YOUR domain — a redirect/
phishing surface.
```

## 6. The scheme-header deception — an http/https downgrade

```text
an unkeyed X-Forwarded-Scheme — the app's absolute URLs use YOUR
scheme — the stored copy's links point to http — a downgrade.
```

## 7. The UA-dependent deception — a per-UA response

```text
an unkeyed User-Agent — the app personalizes on the UA — the stored
copy serves YOUR UA's response to every requester — a mobile-vs-
desktop or a browser-specific confusion.
```

## 8. The language deception — a localized response

```text
an unkeyed Accept-Language — the app localizes on it — the stored
copy serves YOUR language to every requester.
```

## 9. The cookie deception — a per-cookie response

```text
an unkeyed cookie — the app personalizes on it — the stored copy
carries the per-cookie response to every requester.
```

## 10. The charset-XSS injection — the verified card's injection

```text
an unkeyed reflected charset — an injected charset XSS stored in
the cached page — the privileged bot's XSS writes files inside the
container — the chain that reaches the flag.
```

## 11. The X-Original-URL deception — a path-rewrite

```text
an unkeyed X-Original-URL/X-Rewrite-URL — the app honors it — a
rewritten path — the stored copy serves the rewritten response
under the public URL.
```

## 12. The per-shape deception-map — which shape for which surface

```text
an authenticated page + a shared cache   → authenticated-served-anon
a personalized page + a shared cache     → personalized-served-public
an unkeyed reflected header              → injected-response
a path normalization boundary            → route-confusion
an unkeyed Host                          → URL-rewrite
an unkeyed X-Forwarded-Scheme            → scheme-downgrade
an unkeyed User-Agent                    → per-UA confusion
an unkeyed Accept-Language               → localized confusion
an unkeyed cookie                        → per-cookie confusion
an unkeyed X-Original-URL                → path-rewrite
```

## 13. The deception's blast radius — the shared-store effect

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast radius is the URL's requester base —
a public URL poisons every visitor.
```

## 14. The deception's TTL — the expiry question

```text
a stored entry lives until its TTL — the deception persists for the
TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one.
```

## 15. The deception's confirm — the wrong-context serve

```bash
# the anonymous request — the stored copy serves the privileged page
curl "$BASE/settings.html?cb=<unique>"   # anonymous — the privileged page?
#   the privileged content in the anonymous response → deception
```

```text
the deception's confirm is the WRONG-context serve — the privileged
content in the anonymous requester's response — not just a stored
copy.
```
