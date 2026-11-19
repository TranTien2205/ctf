# Class boundary — XS-leaks vs its confusables

The exact line between an XS-leak and the classes it's confused with.

---

## 1. web-xs-leaks vs web-cors — the read-vs-measure split

```text
web-cors   — a fetch READS the response bytes — a real read
             primitive (an ACAO that lets your origin read).
web-xs-leaks — the response is OPAQUE — you MEASURE its shape (a
             frame-count, an error, a timing, a CSS match) — you
             never read the bytes.
the question: can your JS read the response body?
  yes → web-cors (a real read)
  no  → web-xs-leaks (a side-channel measure)
```

## 2. web-xs-leaks vs web-csrf — the read-vs-write split

```text
web-csrf   — the bot WRITES (a state change) — a same-site
             navigation, a form submit, a credentialed POST.
web-xs-leaks — the bot's GET is a READ — you measure its shape.
the question: does the bot's action WRITE state or READ it?
  write → web-csrf
  read + opaque → web-xs-leaks
```

## 3. web-xs-leaks vs web-xss — the JS-in-context split

```text
web-xss    — your JS runs IN THE TARGET's context — it reads the
             DOM directly — a real read primitive.
web-xs-leaks — your JS runs on YOUR origin (the classic shape) or
             doesn't run at all (the sealed shape) — you measure a
             side-channel, never read the DOM.
the question: does your JS run on the TARGET's origin?
  yes → web-xss (a real read)
  no  → web-xs-leaks (a side-channel measure)
```

## 4. web-xs-leaks vs web-cache-poisoning — the store-vs-measure split

```text
web-cache-poisoning — a stored response — you poison a cache that
             serves the victim later — a WRITE to a shared store.
web-xs-leaks — you MEASURE the current response's shape — a
             side-channel read, not a stored write.
the question: do you STORE a response for later, or MEASURE the
             current one?
  store → web-cache-poisoning
  measure → web-xs-leaks
```

## 5. web-xs-leaks vs web-request-smuggling — the smuggle-vs-measure split

```text
web-request-smuggling — a desync between front-end and back-end —
             a smuggled request that reaches a different route.
web-xs-leaks — a side-channel measure of an opaque response — no
             desync, no smuggled request.
the question: is the leak a desync or a side-channel measure?
  desync → web-request-smuggling
  measure → web-xs-leaks
```

## 6. web-xs-leaks vs a JSONP/XSSI endpoint — the serve-vs-measure split

```text
a JSONP endpoint — the server SERVES data AS JavaScript — a script-
             tag read — a real read primitive, not a side-channel.
web-xs-leaks — the response is OPAQUE — you measure its shape.
the question: does the endpoint serve the data as executable JS?
  yes → a real read primitive (JSONP/XSSI)
  no  → web-xs-leaks (a measure)
```

## 7. web-xs-leaks vs a postMessage broadcast — the broadcast split

```text
a postMessage broadcast — the page SENDS data to '*' — a real read
             primitive — the data is transmitted, not inferred.
web-xs-leaks — the response is OPAQUE — you measure its shape.
the question: does the page broadcast the data?
  yes → a real read primitive
  no  → web-xs-leaks (a measure)
```

## 8. web-xs-leaks vs a `*` ACAO — the public-read split

```text
a `*` ACAO — the response IS readable (non-credentialed) — a CORS
             public read — a real read primitive.
web-xs-leaks — the response is OPAQUE — you measure its shape.
the question: is the response readable?
  yes → a CORS question
  no  → web-xs-leaks
```

## 9. The signal-to-class map — which observation names which class

```text
a fetch that READS the body           → web-cors
a bot that WRITES state               → web-csrf
a JS that runs on the TARGET origin   → web-xss
a stored response for a future read   → web-cache-poisoning
a desync front-end/back-end           → web-request-smuggling
a script-tag serve (JSONP)            → a real read primitive
a postMessage '*' broadcast           → a real read primitive
a `*` ACAO public read                → a CORS question
an opaque response + a side-channel   → web-xs-leaks
```

## 10. The deciding test — is the response readable

```js
// the one question that settles it:
fetch('https://t/api/x')
 .then(r=>r.text())
 .then(t=>exfil('READ: '+t))       // a real read → web-cors
 .catch(e=>exfil('OPAQUE'));       // opaque → web-xs-leaks
```

```text
a 'READ' result → web-cors.
an 'OPAQUE' result → web-xs-leaks — the side-channel measure is the
only read available.
```

## 11. The XS-leak signature — the class in one test

```text
an opaque response + a bot whose session you can't read directly +
a side-channel that differs with the content = an XS-leak. the
response is never read — only measured.
```
