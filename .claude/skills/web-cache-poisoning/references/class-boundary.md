# Class boundary — cache-poisoning vs its confusables

The exact line between a cache deception and the classes it's confused with.

---

## 1. web-cache-poisoning vs web-parser-differential — the store-vs-parse split

```text
web-cache-poisoning   — a STORED response served to the wrong
                        context — the cache's key-mismatch.
web-parser-differential— a PARSER difference between front-end and
                        back-end — a routing/normalization confusion.
the question: is the confusion a stored copy or a parse?
  stored → web-cache-poisoning
  parsed → web-parser-differential
```

## 2. web-cache-poisoning vs web-request-smuggling — the store-vs-desync split

```text
web-request-smuggling — a DESYNC between front-end and back-end —
                        a smuggled request reaching a different route.
web-cache-poisoning   — a stored response served to the wrong
                        context — no desync, no smuggled request.
the question: is the leak a desync or a stored copy?
  desync → web-request-smuggling
  stored → web-cache-poisoning
```

## 3. web-cache-poisoning vs web-xs-leaks — the store-vs-measure split

```text
web-xs-leaks          — an OPAQUE response you measure — a side-
                        channel read (a frame-count, an error, a
                        timing).
web-cache-poisoning   — a stored response served to the wrong
                        context — a real serve, not a measure.
the question: is the read a stored copy or a measure?
  stored → web-cache-poisoning
  measured → web-xs-leaks
```

## 4. web-cache-poisoning vs web-xss — the store-vs-injection split

```text
web-xss               — your JS runs IN THE TARGET's context — a
                        real injection.
web-cache-poisoning   — your input's effect is STORED in a cached
                        page — the stored copy carries it — a
                        stored-XSS-like effect through the cache.
the question: is the injection in a live response or a stored copy?
  live → web-xss
  stored → web-cache-poisoning (a stored-XSS through the cache)
```

## 5. web-cache-poisoning vs web-cors — the store-vs-read split

```text
web-cors              — a fetch READS the response bytes — a real
                        read primitive.
web-cache-poisoning   — a stored response served to the wrong
                        context — a serve, not a read.
the question: is the data read directly or served from a cache?
  read → web-cors
  stored-served → web-cache-poisoning
```

## 6. web-cache-poisoning vs web-csrf — the store-vs-write split

```text
web-csrf              — a WRITE (a state change) — a same-site
                        navigation, a form submit, a credentialed POST.
web-cache-poisoning   — a stored response served to the wrong
                        context — a serve, not a write.
the question: is the action a write or a serve?
  write → web-csrf
  stored-serve → web-cache-poisoning
```

## 7. The signal-to-class map — which observation names which class

```text
a fetch that READS bytes              → web-cors
a WRITE                               → web-csrf
a JS that runs on the TARGET origin   → web-xss
a desync front-end/back-end           → web-request-smuggling
a parser difference                   → web-parser-differential
an opaque response + a side-channel   → web-xs-leaks
a stored response served to others    → web-cache-poisoning
```

## 8. The deciding test — is the response stored

```bash
# the one question that settles it — does a stored copy serve the
# response to a different requester
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'  # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   <marker> reflected → stored copy serves YOUR input → cache-poisoning
#   <marker> NOT reflected → no stored copy → a different class
```

```text
a reflected marker from a stored copy → web-cache-poisoning.
a reflection on a MISS → a reflection, not a store → a different class.
```

## 9. The cache-poisoning signature — the class in one test

```text
an unkeyed input + a stored copy + a different requester's serve =
a cache-poisoning. the response is stored once and served to every
requester of the same key — the key-mismatch is the vulnerability.
```

## 10. The confusable deception — a stored-vs-live serve

```text
a stored copy that serves YOUR input to a different requester →
a cache-poisoning (a store).
a response the origin serves only to YOUR request → a reflection
(a live serve, not a store).
```
