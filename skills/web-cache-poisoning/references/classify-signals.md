# Classify signals — the cache-poisoning signals the classifier sees

The signals that name the class — and the confusion that names another.

---

## 1. The cache-presence signals — the cache exists

```text
an X-Cache-Status header     → an nginx cache — a stored-response surface
a CF-Cache-Status header     → a Cloudflare cache — a stored-response surface
an X-Varnish header          → a Varnish cache — a stored-response surface
an X-Served-By header        → a Fastly cache — a stored-response surface
an X-Cache header            → a generic/CloudFront cache
an Age header                → a stored copy's age — a cacheable page
a Via header                 → a proxy chain — a cache in the path
a proxy_cache config         → an nginx cache
a vcl_hash config            → a Varnish cache
```

## 2. The key signals — what's keyed

```text
a Vary header                → the key's discriminator — which headers keyed
a proxy_cache_key template   → the configured key parts
a vcl_hash                   → the hashed request parts
a make_cache_key             → the app's key builder
```

## 3. The unkeyed-input signals — the poisoning vector

```text
an unkeyed reflected header  → the app reflects, the cache ignores — the vector
an unkeyed param             → a stripped param — the vector
an unkeyed cookie            → a cookie not in Vary — the vector
a path-normalization boundary→ a URL the cache and app normalize differently
```

## 4. The deception signals — the privileged page

```text
an authenticated page + a shared cache → a deception surface
a personalized page + a shared cache   → a per-user leak
a Cache-Control: public, max-age       → a cacheable page
```

## 5. The injectable signals — the payload surface

```text
a reflected unkeyed header   → a stored-payload surface
an unkeyed X-Forwarded-Host  → a URL-rewrite surface
an unkeyed Accept-Charset    → a charset-injection surface
an unkeyed User-Agent        → a per-UA confusion surface
```

## 6. The confusable signals — which signals name another class

```text
a fetch that reads bytes              → web-cors
a write                               → web-csrf
a JS that runs on the target origin   → web-xss
a desync front-end/back-end           → web-request-smuggling
a parser difference                   → web-parser-differential
an opaque response + a side-channel   → web-xs-leaks
a stored response served to others    → web-cache-poisoning
```

## 7. The signal-to-class map — the classifier's output

```text
a cache-status header + an unkeyed input + a stored copy serve →
  web-cache-poisoning (a verified class — a chain card exists)
a parser difference + no stored copy → web-parser-differential
a desync + no stored copy → web-request-smuggling
an opaque response + a side-channel → web-xs-leaks
```

## 8. The classifier's use — the chain card

```bash
python3 tools/classify.py --source <dir>
python3 tools/chain_match.py --source <dir> --record <challenge>
# a chain card match → run the card's first_confirming_probe first
```

## 9. The falsifier signals — the dead surface

```text
a keyed input                → a per-input entry → a different class
a MISS reflection            → a reflection → a different class
a no-store page              → a non-cached page → a different class
a 302 to login               → a keyed auth → a different class
```
