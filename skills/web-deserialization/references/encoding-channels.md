# Encoding Channels — the wrappers around the blob

## The layer cake — unwrap in order

A serialized blob usually arrives under 2-3 encodings. The order matters:

```
URL-encode( base64( serialize(obj) ) )       → unwrap: unurl → deb64 → grammar
base64( gzip( serialize(obj) ) )             → deb64 → gunzip → grammar
hex( serialize(obj) )                         → unhex → grammar
url( b64( blob ) ) inside a JSON field       → json → unurl → deb64 → grammar
```

## The wrapper census — what each looks like

| Wrapper | Marker | Unwrap |
|---|---|---|
| base64 | `rO0`,`gAN`,`Tzo`,`BAh`,`AAE`,`/wEP` | `base64 -d` |
| base64url | `-`/`_` instead of `+/` | `base64.urlsafe_b64decode` |
| hex | `[0-9a-f]+` even length | `xxd -r -p` |
| URL-encoded | `%XX` | `urllib.parse.unquote` |
| double-URL | `%25XX` | unquote twice |
| gzip/zlib | `1f 8b` / `78 9c`/`78 da` | `gzip -d`/`zlib.decompress` |
| zlib raw | `78 01` | `zlib.decompress` |
| base64+gzip | `H4sI` | `base64 -d \| gunzip` |
| Java-serialized-in-b64 | `rO0` | `base64 -d` |
| php-in-b64 | `Tzo`/`YToy`/`czo` | `base64 -d` |
| pickle-in-b64 | `gAN`/`gAR`/`gAQ`/`gAU` | `base64 -d` |
| marshal-in-b64 | `BAh` | `base64 -d` |
| .NET-in-b64 | `AAEAAAD`/`/wEP` | `base64 -d` |
| b64 inside JSON string | `{"d":"rO0..."}` | `json` → `b64` |
| b64 inside XML text | `<d>rO0...</d>` | `xml` → `b64` |
| b64 inside JWT payload | `{"obj":"rO0..."}` | `jwt` → `b64` |
| `S:` hex-escape inside PHP | `S:5:"\00"` | php grammar handles it |
| rot13/xor | rare | `tr`/xor-solve |
| PEM armor | `-----BEGIN` | `base64 -d` the body |
| uuencode | `begin 644` | `uudecode` |

## The nested-format reflex — peel until magic bytes

```bash
# always decode twice, check, decode again:
echo -n "$BLOB" | base64 -d | xxd | head -4        # first layer
echo -n "$BLOB" | base64 -d | base64 -d | xxd | head -4   # second
echo -n "$BLOB" | python3 -c "import sys,urllib.parse;print(urllib.parse.unquote(sys.stdin.read()))" | base64 -d | xxd | head -4
echo -n "$BLOB" | base64 -d | gunzip 2>/dev/null | xxd | head -4
echo -n "$BLOB" | xxd -r -p | xxd | head -4
```

## The content-type hint — what the envelope claims

```
Content-Type: application/x-java-serialized-object   → OIS stream
Content-Type: application/octet-stream               → generic binary
Content-Type: text/plain / application/json          → wrapped b64
Content-Type: application/x-php-serialized           → rare, PHP
Content-Type: application/x-java-serialized-object   → OIS
X-Java-Serialized-Object: <b64>                      → OIS in header
Content-Type: text/xml                               → XStream/XMLDecoder
Content-Type: application/x-yaml / text/yaml         → typed-tag sink
```

`Content-Type` is a hint, not a contract — a body can be the wrong format
for its type; the magic bytes decide.

## The "charset/transfer" smuggling — the channel-mangle

A channel that mangles bytes breaks the grammar — the wrapper is the fix:

- **7-bit/ASCII channel** → base64 or hex the blob
- **cookie-safe** → base64url (`-_` not `+/`, no `=` pad)
- **JSON field** → the blob is a string inside JSON — quotes/backslashes
  in it break JSON → base64 it first
- **XML text** → `<`/`>`/`&` in the blob break XML → base64 or CDATA
- **URL param** → `+`/`%`/`&`/`=` break the param → url-encode or base64url
- **YAML scalar** → `:`/`#`/leading-space break the scalar → `|` block or b64
- **a `length` prefix in a frame** → the frame's declared len must match —
  a wrapper that changes length breaks the frame unless you recount

## The frame-length trap

Some wrappers carry a length the receiver trusts:

```
[len:u32][aced0005...]            — the u32 must equal the stream length
{"len":123,"data":"<b64>"}         — a declared-length field
Cookie: x=<b64>; sig=<hmac>        — sig covers the b64's bytes
```

Wrap + resend with a WRONG declared length → the frame may truncate your
blob mid-grammar → `StreamCorruptedException`/`truncated` — different
error than "not deserializing". Keep the wrapper's length consistent.

## The double-wrap the app expects

Some apps do `unserialize(base64_decode($x))` — the blob MUST be b64 to
parse. Send it raw → `unserialize(): Error` on the raw b64 string. Read
the wrapper chain in source before crafting:

```php
unserialize($_COOKIE['u'])                        → send raw serialize()
unserialize(base64_decode($_COOKIE['u']))         → send b64(serialize)
unserialize(gzuncompress(base64_decode($_GET['x']))) → b64(gzip(serialize))
```

## The signature-wrap ordering

```
sign(serialize(obj))              → HMAC over raw bytes
sign(base64(serialize(obj)))      → HMAC over the b64 string
base64(encrypt(serialize(obj)))   → encrypted then armored
```

The signature input is whatever the code feeds `hash_hmac`/`sign` — the
wrapper inside or outside changes the MAC input. Forging means wrapping in
the SAME order the code does.

## Output to record

- The exact wrapper chain in order (url→b64→gzip→grammar)
- Where each layer is added/removed in source
- The verbatim blob after each unwrap step
