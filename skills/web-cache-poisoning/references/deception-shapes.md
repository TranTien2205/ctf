# Deception shapes — the cache-deception variants

Every way a stored response reaches the wrong context.

---

## 1. The authenticated-page-served-anonymously — the verified card

```text
an authenticated page cached under a URL the anonymous requester
also fetches — the cache keys on the URL, not the auth state — the
stored response is the privileged page served to anyone.
```

```bash
# the card's probe — an authenticated GET, then an anonymous GET
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores it
curl "$BASE/settings.html?cb=<unique>"                     # anonymous — HIT?
#   the anonymous request returns the authenticated page → the
#   cache serves the privileged copy anonymously
```

## 2. The personalized-page-served-publicly — the per-user leak

```text
a personalized page (a profile, a dashboard, a session-scoped)
cached under a shared URL — the stored copy serves YOUR personalized
content to every requester — a session-data leak.
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

## 5. The param-append deception — a keyed-param confusion

```text
a keyed param the app ignores vs an unkeyed param the app reads —
the deception is in which param carries the effect and which carries
the key.
```

## 6. The Host-header deception — the URL-rewrite leak

```text
an unkeyed Host/X-Forwarded-Host — the app's absolute URLs and
redirects use YOUR host — the stored copy's links point to YOUR
domain — a redirect/phishing surface.
```

## 7. The scheme-header deception — an http/https downgrade

```text
an unkeyed X-Forwarded-Scheme — the app's absolute URLs use YOUR
scheme — the stored copy's links point to http — a downgrade or a
mixed-content surface.
```

## 8. The UA-dependent deception — a per-UA response

```text
an unkeyed User-Agent — the app personalizes on the UA — the stored
copy serves YOUR UA's response to every requester — a mobile-vs-
desktop or a browser-specific confusion.
```

## 9. The language deception — a localized response

```text
an unkeyed Accept-Language — the app localizes on it — the stored
copy serves YOUR language to every requester.
```

## 10. The cookie deception — a per-cookie response

```text
an unkeyed cookie — the app personalizes on it — the stored copy
carries the per-cookie response to every requester.
```

## 11. The per-shape deception-map — which shape for which surface

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
```

## 12. The deception's blast radius — the shared-store effect

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast radius is the URL's requester base —
a public URL poisons every visitor.
```

## 13. The deception's TTL — the expiry question

```text
a stored entry lives until its TTL — the deception persists for the
TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one.
```
