# Multipart Spec — the wire format deep enough to break it

## The wire form, byte-precise

```
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=BOUNDARY
Content-Length: N

--BOUNDARY\r\n
Content-Disposition: form-data; name="textfield"\r\n
\r\n
value\r\n
--BOUNDARY\r\n
Content-Disposition: form-data; name="f"; filename="x.txt"\r\n
Content-Type: text/plain\r\n
\r\n
<file bytes>\r\n
--BOUNDARY--\r\n
```

Facts the parsers disagree on:

- preamble/epilogue around the boundaries — text before the first `--B` and
  after `--B--` is ignored by spec; lenient parsers read it, strict reject
- delimiter is `\r\n--B` — the FIRST `--B` at body start has no leading CRLF
- `boundary` may be quoted: `boundary="B"` — parsers must strip quotes
- boundary max 70 chars, charset-restricted — some parsers accept more
- header folding `obs-fold` is deprecated but many parsers still unfold
- part headers end at `\r\n\r\n`; a part with NO headers has just `\r\n` then data
- `Content-Transfer-Encoding` is deprecated in multipart/form-data — parsers
  that honor `base64`/`quoted-printable` differ

## The Content-Disposition grammar

```
Content-Disposition: form-data; name="f"; filename="x.txt";
                    filename*=UTF-8''x%2Etxt
```

- `name` REQUIRED per part — missing/duplicate behavior varies
- `filename` is a quoted-string — `\` escapes `"` and `\` INSIDE quotes:
  `filename="a\"b"` parses as `a"b` in compliant parsers, literally in naive
- `filename*` is RFC 5987 extended — `UTF-8''<pct-encoded>` — the WINNING
  field when both present per RFC 6266; naive parsers ignore it
- unknown params are ignored — `filename="x"; z="y"` fine

## Per-parser quirks — the divergence goldmine

| Parser | Quirk |
|---|---|
| PHP `$_FILES` | takes LAST same-name part; `name="f[]"` builds arrays; `filename` raw; `MAX_FILE_SIZE` honored client+server |
| Python `cgi.FieldStorage` | deprecated; reads `filename*`? honors first occurrence; `name` collisions list |
| Werkzeug | `request.files` — last-wins; `filename` parsed with quote handling; honors `filename*`? newer versions do |
| Node `busboy` | streams parts in order — first-wins for single-slot consumers; emits `limit` events |
| `multer` | builds `req.file` (first) / `req.files` array; filename default `fieldname-rand` |
| `formidable` | `files.file[0]` array or object — config-dependent; `filename` honoring varies |
| Java Servlet `Part` | `getSubmittedFileName` — spec says strip path; impls differ on `..` |
| ASP.NET `IFormFile` | `FileName` strips path per spec — `..` removed? Verify — `ContentDispositionHeaderValue` normalizes |
| Go `mime/multipart` | `FormName`/`FileName` — strips path in `FileName`; honors `filename*` |
| Rust `multer` | `file_name()` returns full sent name (no strip) — traversal intact |

"Strips path" means `../../x` → `x` — check which side of the check-vs-
store pair uses the sanitized vs raw name.

## Encoding inside part headers — the spaces parsers miss

- `filename="x.php" ` trailing space inside quotes — stripped or kept?
- `filename=x.php` unquoted — a token, stops at `;`/space — `x.php;y`
  truncates
- `filename="x\t.php"` tab inside quotes
- `filename="x.php;param=v"` semicolon inside quotes — is it a param
  boundary or part of the name? Compliant: inside quotes it's literal;
  naive split-on-`;` truncates to `x.php`
- non-ASCII `filename` bytes — raw UTF-8 vs `filename*`

## Mixed content — file + text fields interplay

```
name="f"; filename="x.php"     → file part
name="f"                       → text field with same name
```

PHP merges them into `$_FILES`/`$_POST` separately — both exist. A
validator reading `$_POST['f']` sees the text while `$_FILES['f']` holds
the upload. Other stacks unify them into one list — the validator's pick
differs from the store's.

## The `MAX_FILE_SIZE` hidden-field trick

PHP honors `MAX_FILE_SIZE` in the form BEFORE the file part — client-side
hint but PHP also enforces it server-side in some SAPIs. It's not a
bypass — it's a signal the form came from PHP-era code.

## Testing tools

```bash
# hand-crafted body through http_probe — control every byte:
python3 tools/web/http_probe.py ... --body $'--X\r\nContent-Disposition: form-data; name="f"; filename="x.php"\r\nContent-Type: image/png\r\n\r\n<?php ...?>\r\n--X--\r\n'

# curl -F for the common cases:
curl -F 'f=@x.php;type=image/png' -F 'f=@x.jpg' URL      # two parts same name
curl -F 'f=@x.php;filename=a.png' URL                    # filename rewrite
curl -F 'f=@x.php;filename*='"'"'UTF-8'"'"''x%2Ephp' URL # filename* (curl needs manual body)
```

`filename*` isn't supported by `curl -F` — hand-craft the body.

## Output to record

- the parser pair identified + the byte-level divergence that beat them
