# Summary — cache-poisoning in one page

The whole class, condensed.

---

## The class in one line

A cache stores YOUR response under a URL the victim requests — the
stored copy serves YOUR input's effect to every requester.

## The detection — the cache surface

```bash
# the cache status — a HIT/MISS/AGE header
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish'
# the Vary — the key's discriminator
curl -sI "$BASE/" | grep -i 'vary'
# the proxy's key config
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|make_cache_key' <src> | head
```

## The unkeyed inputs — the poisoning vectors

```
an unkeyed header        — the app reflects, the cache ignores
an unkeyed param         — a utm, fbclid, a tracking param
an unkeyed cookie        — a cookie not in Vary
a path-normalization     — a URL the cache and app normalize differently
an authenticated+shared  — an authenticated page served anonymously
```

## The confirm — the three-part evidence

```
- the probe request STORED — a HIT on the second identical request
- the keyed input left OUT of the cache key — the unkeyed input
- the reflected value reaching a response the victim receives — the
  clean request reflects the marker
a reflected header on a MISS is not a poisoning.
```

## The deception — the authenticated-page-served-anonymously

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## The blast radius — the shared-store effect

```
a poisoned entry is served to EVERY requester of the URL until it
expires — a public URL poisons every visitor — use a harmless
marker; keep the window short; clean up.
```

## The falsifier

```
the input IS part of the cache key — the stored copy is keyed per-
input — the stored response serves YOUR input only to YOUR requests
→ a different class.
no front-end cache → no stored response → a different class.
a reflected marker on a MISS → a reflection, not a poisoning.
```

## The confusables

```
a fetch READS bytes → web-cors | a WRITE → web-csrf
a desync → web-request-smuggling | a parser diff → parser-differential
an opaque response + a side-channel → web-xs-leaks (a measure)
a stored response served to others → web-cache-poisoning (a store)
```

## The per-vector selection

```
an unkeyed reflected header    → the header vector
an unkeyed query param         → the param vector
an unkeyed Host                → the host vector
an unkeyed X-Forwarded-Scheme  → the scheme vector
an unkeyed User-Agent          → the UA vector
an unkeyed cookie              → the cookie vector
a path normalization boundary  → the path-confusion vector
an authenticated + shared cache → authenticated-served-anonymously
```

## The verified card — the HTB Encodecept shape

```
an authenticated page cached + served anonymously + an unkeyed
reflected charset XSS stored in the cached page + a marshal
deserialization RCE — the privileged bot's XSS writes files inside
the container.
```
