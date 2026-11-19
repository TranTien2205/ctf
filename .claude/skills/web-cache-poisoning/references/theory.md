# Theory — why cache poisoning exists and why it works

The mechanism behind every cache deception.

---

## 1. The cache's role — a stored-response layer

```text
a cache sits in front of the application — it stores responses and
serves them to later requests without hitting the origin. the
whole mechanism: the stored response is SHARED across requesters —
a response stored once is served to every requester of the same
key.
```

## 2. The cache key — which request shares which copy

```text
the cache key = the set of request parts that determine which stored
copy serves a request. the default is the URL (scheme + host + URI);
headers are unkeyed unless the config adds them or the response
carries Vary. a Vary header names the request headers that vary the
stored entry.
```

## 3. The unkeyed input — the poisoning vector

```text
an unkeyed input = a request part the APPLICATION reads (reflects,
redirects on, personalizes on) but the CACHE key IGNORES. the
stored response carries YOUR input's effect — every requester of
the same URL gets YOUR poisoned copy. the vulnerability is the
mismatch: the app reads what the cache ignores.
```

## 4. Why the stored copy serves YOUR input to everyone

```text
the cache stores YOUR request's response under the key — the URL —
and serves it to every requester of the same key. YOUR input's
effect is baked into the stored copy — a requester who never sent
YOUR input gets YOUR response.
```

## 5. Why the Vary header matters — the key's discriminator

```text
a Vary: Cookie header keys the entry on the cookie — a per-session
copy — YOUR input's effect is in YOUR copy only, not a shared one.
no Vary on a header = that header is unkeyed — the stored response
serves YOUR input to every requester.
```

## 6. Why the authenticated-page-served-anonymously works

```text
an authenticated page cached under a URL the anonymous requester
also fetches — the cache keys on the URL, not the auth state — the
stored copy is the privileged page served to anyone. the deception:
the cache doesn't distinguish 'your authenticated copy' from 'the
anonymous requester's copy' — one URL, one stored response.
```

## 7. Why the path-normalization deception works

```text
a path the cache and the app normalize differently — the cache
stores it under one URL; the app routes it to a different handler —
the stored copy's URL is the victim's URL, the response is YOUR
request's. a static-looking URL serves the dynamic response.
```

## 8. Why the MISS-vs-HIT distinction matters — the stored-copy requirement

```text
a MISS — the response came from the origin, not the cache — a
reflected marker on a MISS is a REFLECTION, not a poisoning. a HIT
— the response came from the stored copy — the marker's reflection
came from the cache — the poisoning. the whole class requires the
stored copy to serve YOUR input to a different requester.
```

## 9. Why the blast radius is the URL's requester base

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the blast radius is the URL's requester base — a public
URL poisons every visitor; a niche URL poisons a few. the shared
store is the whole vulnerability.
```

## 10. Why the TTL bounds the persistence

```text
the stored entry lives until its TTL — the deception persists for
the TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one. the TTL bounds the blast radius's duration.
```

## 11. Why the unkeyed-input check is the confirm's gate

```text
the unkeyed input is the whole vulnerability — a keyed input keys
the entry per-value — the stored response serves YOUR input only
to YOUR requests — a cache-buster defeats the poisoning. no unkeyed
input = no shared poisoning = a different class.
```

## 12. Why the deception needs a separate class — the stored-response

```text
a cache deception isn't a reflection (a reflected marker on a MISS)
— it's a STORED response served to the wrong context — the stored
copy is the evidence, not the reflection. the class boundary: a
response the cache stores and serves to others vs a response the
origin serves only to you.
```
