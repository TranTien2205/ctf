# Blob Wraps — the encoding layers around the serialized stream

## The point — the wire format is never the raw stream

A serialized object almost never travels as raw bytes — it's base64'd,
URL-encoded, hex'd, JSON-wrapped, compressed, encrypted, or signed. The
fingerprint lives under the wrap; peel the layers in order.

## The wrap stack — outermost first

```
URL-encoding (%)              → urldecode
Base64                        → b64decode (url-safe variant: -_ for +/)
Hex                           → unhex
JSON string                   → json.loads → the inner value
gzip/deflate/zlib             → decompress
encryption (AES/Fernet/XOR)   → decrypt — needs the key
signature (HMAC trailing)     → validate/strip — the sig is separate
```

A blob is usually `urlencode(b64(stream))` or `b64(stream)+"."+b64(sig)` —
peel each layer and fingerprint the inner bytes.

## The fingerprint AFTER peeling — the order of operations

```bash
# 1. urldecode if %-heavy
# 2. b64decode if b64-charset
# 3. gunzip if magic 1f 8b
# 4. fingerprint the raw bytes:
#    aced→Java  O:/a:→PHP  \x80\x03→pickle  \x04\x08→Marshal
#    00 01...→BinaryFormatter  {"→JSON  <!→XML  !!→YAML
```

## The double-wrap — the classic challenge shape

```
outer: JSON {"data":"<b64>","sig":"<hmac>"}
  inner b64: O:8:"User":...
```

Peel JSON → b64 → PHP stream. The `sig` covers the b64 — flip inside the b64
and re-sign only if the key is known (`signature-bypass.md`).

## The compression tell — magic bytes under the b64

```
1f 8b           → gzip
78 9c / 78 da   → zlib/deflate
42 5a 68 (BZh)  → bzip2
fd 37 7a 58 5a  → xz
28 b5 2f fd     → zstd
```

A b64 blob decoding to `1f 8b` → `gzip -d` → THEN the serialize fingerprint.

## The encryption tell — when no fingerprint emerges

- uniform-random bytes, no magic → encrypted (AES-CTR/CBC/GCM) or raw binary
- a fixed-size block multiple (16/32) → block cipher
- `gAAAAA` prefix → Fernet (Python)
- `$2a$`/`$2y$` → a bcrypt hash, not a blob
- a 32/64-hex tail → HMAC signature, not part of the payload

Encrypted blob → the KEY is the target (`key-hunt-deep.md`), not the format.

## The signed-blob anatomy — where the sig lives

```
<blob>.<sig>                    → split on the last dot
{"data":"<blob>","sig":"<hex>"} → the sibling field
<blob>+<32/64-hex tail>         → trailing HMAC
cookie: "s:<blob>.<sig>"        → express/itsdangerous shape
__VIEWSTATE + __EVENTVALIDATION → the MAC is inside the LosFormatter blob
```

The sig bytes are NOT part of the serialized stream — don't feed them to
the parser.

## The charset traps — decode errors that mean something

- `b64decode` fails → not b64 — try url-safe b64 (`-_` chars) or raw
- `urldecode` leaves `%` → double-encoded — decode twice
- a `+` in the blob that decodes wrong → `+` is space in form-encoding —
  the blob needs `%2B` or url-safe b64
- a decoded blob with high-entropy + no magic → compressed or encrypted

## The polyglot wrap — a blob that survives re-wrap

`polyglot-deser.md` — a payload whose inner stream stays valid after the
app's own re-encoding (the app b64-encodes your input, so send RAW stream
bytes, not pre-b64'd).

## The "peel, don't guess" discipline

```bash
python3 - <<'PY'
import base64,urllib.parse,zlib
b="<the blob>"
for step in ["url","b64","hex","raw"]:
    try:
        if step=="url": b=urllib.parse.unquote(b); continue
        if step=="b64": b=base64.b64decode(b+"=="); continue
        if step=="hex": b=bytes.fromhex(b); continue
    except Exception: pass
    break
print(b[:20])   # fingerprint these bytes
PY
```

Then fingerprint — the magic bytes of the INNER layer pick the module.

## Output to record

- The wrap layers found, in order (url→b64→gzip→stream)
- The magic bytes at the core + the format module they route to
- Whether a signature or encryption layer exists (→ the key problem)
