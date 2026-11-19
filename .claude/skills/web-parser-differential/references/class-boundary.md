# Class boundary — parser-differential vs its confusables

The exact line between a parse differential and the classes it's confused with.

---

## 1. web-parser-differential vs web-request-smuggling — the parse-vs-desync split

```text
web-parser-differential — a PARSE difference between front-end and
                        back-end — a routing/normalization confusion.
web-request-smuggling   — a DESYNC between front-end and back-end —
                        a smuggled request reaching a different route.
the question: is the confusion a parse or a desync?
  parse → web-parser-differential; desync → web-request-smuggling
```

## 2. web-parser-differential vs web-cache-poisoning — the parse-vs-store split

```text
web-parser-differential — a PARSE difference — a front-end and a
                        back-end parse differently.
web-cache-poisoning     — a STORED response served to the wrong
                        context — the cache's key-mismatch.
the question: is the confusion a parse or a store?
  parse → web-parser-differential; stored → web-cache-poisoning
```

## 3. web-parser-differential vs web-host-header — the parse-vs-rewrite split

```text
web-host-header         — a Host-header manipulation — a rewritten host's
                        effect in YOUR request.
web-parser-differential — a front-end/back-end parse difference — a
                        proxy-header trust check.
the question: is the confusion a host-rewrite or a trust check?
  host-rewrite → web-host-header; trust check → web-parser-differential
```

## 4. web-parser-differential vs web-csrf — the parse-vs-write split

```text
web-csrf                — a WRITE (a state change) — a navigation, a
                        form submit, a credentialed POST.
web-parser-differential — a front-end/back-end parse difference — a
                        trust check, not a write.
the question: is the action a write or a parse?
  write → web-csrf; parse → web-parser-differential
```

## 5. web-parser-differential vs web-xss — the parse-vs-injection split

```text
web-xss                 — your JS runs IN THE TARGET's context — a real
                        injection.
web-parser-differential — a front-end/back-end parse difference — a
                        trust check, not an injection.
the question: is the confusion an injection or a parse?
  injection → web-xss; parse → web-parser-differential
```

## 6. web-parser-differential vs web-auth-session — the parse-vs-session split

```text
web-auth-session        — a session/token check — a JWT, a session
                        cookie, a signature.
web-parser-differential — a proxy-header trust check — a header the
                        app trusts the proxy to set.
the question: is the check a session or a proxy header?
  session → web-auth-session; proxy-header → web-parser-differential
```

## 7. web-parser-differential vs web-logic-flaw — the parse-vs-logic split

```text
web-logic-flaw          — a business-logic flaw — a missing check, a
                        wrong-state confusion.
web-parser-differential — a front-end/back-end parse difference — a
                        proxy-header trust check.
the question: is the flaw a logic or a parse?
  logic → web-logic-flaw; parse → web-parser-differential
```

## 8. The signal-to-class map — which observation names which class

```text
a fetch that reads bytes              → web-cors
a write                               → web-csrf
a JS that runs on the target origin   → web-xss
a desync front-end/back-end           → web-request-smuggling
a stored copy served to others        → web-cache-poisoning
a proxy-header trust check            → web-parser-differential
a session/token check                 → web-auth-session
a host-rewrite                        → web-host-header
a business-logic flaw                 → web-logic-flaw
```

## 9. The deciding test — is the confusion a parse

```bash
# the one question — does the proxy strip its own header → the app's
# check reads a different value
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
#   the proxy strips X-Real-IP → the app's check reads the missing
#   header → a parse differential
#   the header passes through → a different class
```

## 10. The class signature — the parser-differential in one test

```text
a front-end that parses differently → a parser-differential (a parse).
a stored copy that serves YOUR input → a cache-poisoning (a store).
a desync → a request-smuggling (a desync).
```
