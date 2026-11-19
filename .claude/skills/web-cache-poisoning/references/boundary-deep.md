# Boundary deep — the class's edge, exhaustively

The exact line between a cache-poisoning and every confusable class.

---

## 1. web-cache-poisoning vs web-parser-differential — the store-vs-parse split

```text
web-cache-poisoning   — a STORED response served to the wrong context —
                        the cache's key-mismatch.
web-parser-differential— a PARSER difference between front-end and
                        back-end — a routing/normalization confusion.
the question: is the confusion a stored copy or a parse?
  stored → web-cache-poisoning; parsed → web-parser-differential
```

## 2. web-cache-poisoning vs web-request-smuggling — the store-vs-desync split

```text
web-request-smuggling — a DESYNC between front-end and back-end — a
                        smuggled request reaching a different route.
web-cache-poisoning   — a stored response served to the wrong context —
                        no desync, no smuggled request.
the question: is the leak a desync or a stored copy?
  desync → web-request-smuggling; stored → web-cache-poisoning
```

## 3. web-cache-poisoning vs web-xs-leaks — the store-vs-measure split

```text
web-xs-leaks          — an OPAQUE response you measure — a side-channel
                        read.
web-cache-poisoning   — a stored response served to the wrong context —
                        a real serve, not a measure.
the question: is the read a stored copy or a measure?
  stored → web-cache-poisoning; measured → web-xs-leaks
```

## 4. web-cache-poisoning vs web-xss — the store-vs-injection split

```text
web-xss               — your JS runs IN THE TARGET's context — a real
                        injection.
web-cache-poisoning   — your input's effect is STORED in a cached page —
                        the stored copy carries it — a stored-XSS-like
                        effect through the cache.
the question: is the injection in a live response or a stored copy?
  live → web-xss; stored → web-cache-poisoning
```

## 5. web-cache-poisoning vs web-cors — the store-vs-read split

```text
web-cors              — a fetch READS the response bytes — a real read.
web-cache-poisoning   — a stored response served to the wrong context —
                        a serve, not a read.
the question: is the data read directly or served from a cache?
  read → web-cors; stored-served → web-cache-poisoning
```

## 6. web-cache-poisoning vs web-csrf — the store-vs-write split

```text
web-csrf              — a WRITE (a state change) — a navigation, a form
                        submit, a credentialed POST.
web-cache-poisoning   — a stored response served to the wrong context —
                        a serve, not a write.
the question: is the action a write or a serve?
  write → web-csrf; stored-serve → web-cache-poisoning
```

## 7. web-cache-poisoning vs a reflection — the store-vs-live split

```text
a reflection          — the origin serves YOUR input to YOUR request —
                        a live serve, not a store.
web-cache-poisoning   — a stored copy serves YOUR input to a different
                        requester — a shared store, not a live serve.
the question: is the response stored (a HIT) or live (a MISS)?
  stored → web-cache-poisoning; live → a reflection
```

## 8. web-cache-poisoning vs web-host-header — the store-vs-rewrite split

```text
web-host-header       — a Host-header manipulation — a rewritten host's
                        effect in YOUR request.
web-cache-poisoning   — a stored response served to the wrong context —
                        a shared store, not a per-request rewrite.
the question: is the effect stored or per-request?
  stored → web-cache-poisoning; per-request → web-host-header
```

## 9. The deciding test — is the response stored

```bash
# the one question — does a stored copy serve the response to a
# different requester
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → stored copy serves YOUR input → web-cache-poisoning
#   NOT reflected → no stored copy → a different class
```

## 10. The class signature — the cache-poisoning in one test

```text
an unkeyed input + a stored copy + a different requester's serve =
a cache-poisoning. the response is stored once and served to every
requester of the same key — the key-mismatch is the vulnerability.
```
