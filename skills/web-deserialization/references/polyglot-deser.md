# Polyglot Deserialization — blobs that are two formats at once

## The idea — one blob, two valid parses

A polyglot is a byte string that parses *correctly* as two different
things — the WAF/proxy/front-end reads one format, the backend's
deserializer reads another. The checker's grammar and the parser's grammar
differ; your payload is valid in both.

## The PHP `S:`+`s:` confusion — escaping type-confusion

`s:` is a plain string; `S:` is the escaped-string type. A filter that
mangles `'`/`\` sees an `s:` that can't carry the byte — but `S:` escapes
every byte as `\xNN` so the byte is never literal:

```
s:6:"a'b\c";      → breaks through addslashes — the ' gets slashed
S:6:"\61\27\62\5c\63";   → same bytes, no literal ' or \ in the stream
```

The mangle only fires on `s:`-typed content — `S:` smuggles the payload
through the same grammar.

## The `O:+` signed-length polyglot

```
O:4:"User":...       regex /O:\d+:"/ blocks
O:+4:"User":...      PHP accepts the + — regex misses it
O:04:"User":...      leading-zero padding — also accepted
```

## The unicode-length lie (PHP)

Some PHP builds compute `s:` lengths in *bytes* while a validator counts
*characters* — a multibyte char that is 1 char but 3 bytes lets you lie
about the length inside the grammar. The `S:` type sidesteps this entirely
(hex-escape is always one byte).

## The JSON-inside-PHP wrapper

```json
{"data":"O:8:\"User\":2:{s:4:\"name\";s:5:\"admin\";}"}
```

A JSON-typed body whose *value* is a PHP-serialized string — the WAF sees
valid JSON; `unserialize` sees valid PHP. Two valid parses, one byte string.
Delivered whenever the app does `unserialize(json_decode($_POST)['data'])`.

## The phar/image polyglot — the workhorse

`archive_gen.py phar` emits a blob that is:

```
GIF89a\x..\x01\x00        → getimagesize says "valid GIF"
<?php __HALT_COMPILER(); ?> → phar stub parses
[manifest + metadata]     → phar:// metadata → unserialize
```

One file passes `getimagesize`/`finfo`/`exif_imagetype` AND deserializes
via `phar://`. The image check and the phar parser see different valid
objects in the same bytes.

## The gzip-in-a-field polyglot

A JSON field the app `gzuncompress`es then unserializes:

```
{"d":"<b64(gzip(serialize))>"}
```

The WAF scans the base64/JSON — the real grammar lives inside the gzip.
The deserializer never sees the wrapper, the WAF never sees the grammar.

## The double-serialization matryoshka

```
a:1:{i:0;O:8:"User":1:{s:4:"data";s:100:"O:8:\"Inner\":1:{...}";}}
```

An outer `User` whose `data` prop is ITSELF a serialized string — if the
app unserializes twice (or `maybe_unserialize` on a stored field), the
inner `Inner` object fires on the second pass. Some filters check only the
outer grammar.

## The "JWT payload is a serialized blob" shape

```json
{"alg":"HS256"}.{"obj":"O:8:\"User\":..."}.sig
```

The JWT payload is `application/json` — but a FIELD inside carries PHP
serialize. `alg=none`/confusion forges the JWT; the field's value hits the
deserializer. Two formats, two checks, one byte string.

## The `format` header-vs-body confusion

```
Content-Type: application/json          ← WAF inspects as JSON
Body: aced0005 <binary>                  ← backend reads as Java OIS
```

Some apps dispatch on the *body shape* not the `Content-Type` — the WAF
routes by the header, the parser by the magic bytes. A
`Content-Type: application/octet-stream` hiding `O:` PHP, or a
`text/xml` hiding a `aced` stream, is the same trick.

## The `\x00`-truncation polyglot (PHP/C-string boundary)

```
O:4:"User":...{}\x00TRAILING-PICKLE-BYTES
```

A `unserialize` parser stops at the grammar end — the trailing bytes are
ignored. A C-string-aware layer truncates at `\x00`. Two parsers, two
ends, one blob — the second parser sees the tail you smuggled.

## The multi-endpoint type confusion

```
POST /api/json   {"obj":"<b64 blob>"}    → json_decode → unserialize
POST /api/bin    <raw blob>              → unserialize directly
```

Two endpoints, two format checks — the same blob is delivered through
whichever checker's grammar it passes.

## The `p0` ASCII pickle inside a strict-ASCII channel

A `pickle.dumps(obj,0)` is pure ASCII — it fits inside a
`Content-Type: text/plain` field, a cookie that rejects high bytes, an
XML text node. The binary-format check never sees it because there IS no
high byte.

## The "which parser won" question — the diagnostic

When a blob is both-valid, WHICH parse runs decides whether your gadget
fires. The discriminator:

- the **first** parser to consume the bytes decides — the WAF's JSON check
  runs before the app's unserialize
- a body that fails JSON validation never reaches the PHP unserialize
- a body the proxy rejects on `Content-Type` never reaches the app

The polyglot only works when BOTH parsers accept it — test each layer
independently first.

## Output to record

- The two formats the blob satisfies
- Which layer accepts which parse (WAF vs app)
- The verbatim response proving the *deserializer's* parse won
