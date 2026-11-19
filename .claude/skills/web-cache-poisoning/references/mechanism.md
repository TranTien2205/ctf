# Mechanism — how cache poisoning works, at the protocol level

The complete mechanism — the key-mismatch model.

---

## 1. The cache model — a stored response per-key

```text
a cache stores a response per-key — every requester of the same key
gets the same stored copy — the cache trades a fresh fetch for a
stored serve — the shared copy is the vulnerability.
```

## 2. The key-mismatch — the unkeyed input

```text
the cache key = the request parts that determine which stored copy
serves a request:
- the URL (the default key — scheme + host + path + query)
- the Vary'd headers (the headers named in Vary)
- the configured key parts (proxy_cache_key, vcl_hash)
everything NOT in the key is an unkeyed input — the stored response
carries its effect to every requester.
```

## 3. The read-but-not-keyed surface — the poisoning vector

```text
the vulnerability's precondition: a request part the app READS
(reflects, redirects on, personalizes on) but the cache key IGNORES.
the stored copy carries the unkeyed input's effect — every requester's
copy serves it.
```

## 4. The two-request mechanics — the store + the serve

```text
request 1 — the poison request: send the unkeyed input → the origin
            reflects it → the cache stores the response under the key
request 2 — the serve request: a clean request for the same key →
            the cache serves the stored copy → the stored copy carries
            YOUR input → the deception
```

## 5. The deception mechanics — the authenticated-page shape

```text
an authenticated page cached under a shared URL — the cache keys on
the URL, not the auth state — the stored copy is the privileged page —
an anonymous request for the same key gets the privileged copy — the
auth state wasn't in the key.
```

## 6. The injection mechanics — the stored-payload shape

```text
an unkeyed reflected input carries a payload — a JS, a redirect, a
host-rewrite — the stored copy carries YOUR injected content — every
requester's copy serves it — a stored-XSS-like effect.
```

## 7. The persistence mechanics — the TTL

```text
a stored entry lives until its TTL — the deception persists for the
TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one. the TTL is min(the response's max-age, the proxy's
configured TTL).
```

## 8. The blast mechanics — the requester base

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast is the URL's requester base — a
public URL poisons every visitor; a cachebuster URL poisons only your
key's requests.
```

## 9. The falsifier mechanics — the boundary

```text
the attack fails if:
- the input IS part of the cache key — a per-input entry, not shared
- no front-end cache — no stored copy to poison
- a Cache-Control: no-store/private — the page isn't cached
- a reflected marker on a MISS — a reflection, not a store
```

## 10. The class mechanics — the stored-vs-live serve

```text
a stored copy that serves YOUR input to a different requester → a
cache-poisoning (a store).
a response the origin serves only to YOUR request → a reflection (a
live serve, not a store).
```
