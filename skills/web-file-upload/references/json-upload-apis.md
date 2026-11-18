# JSON Upload APIs — when the file arrives as JSON, not multipart

## The shape — the "upload" is a JSON field

```json
POST /api/files
{"filename": "x.php", "content": "PD9waHAgcGhwaW5mbygpOyA/Pg==", "mime": "image/png"}
```

No multipart parser, no `$_FILES` — the app reads `filename` + `content`
(base64/hex/raw string) and writes it. The checks live in JSON-schema,
the store is hand-written.

## Common field shapes

```json
{"file": {"name": "x.png", "data": "<b64>"}}
{"attachment": {"filename": "x.png", "body": "<b64>", "contentType": "..."}}
{"files": [{"name": "x.png", "content": "<b64>"}]}
{"image": "data:image/png;base64,<b64>"}
{"upload": {"path": "x.png", "b64": "..."}}
{"document": "<b64>", "name": "x.pdf", "format": "pdf"}
```

Field names to fuzz: `filename`, `name`, `path`, `file`, `data`,
`content`, `body`, `b64`, `base64`, `bytes`, `mime`, `contentType`,
`type`, `format`, `ext`, `attachment`, `image`, `document`, `upload`.

## What changes vs multipart

- `Content-Type: application/json` — no boundary parser; a WAF that only
  scans multipart misses entirely
- `filename` is a plain string — escape/quote games don't apply; the
  sanitizer is whatever string ops the app runs
- per-part `Content-Type` is a field (`mime`/`contentType`) — pure client
  claim
- `data:` URIs parse `mime` + `b64` — `data:image/png;base64,<php>` — the
  mime is inside the value, and the base64 may carry the payload with
  padding tricks (`;charset=`, `;name=x.php` params inside the URI)

## The new tricks JSON opens

- **`filename` as a path string** — `"filename": "../../x.php"` — the
  traversal is a plain string, no multipart quoting needed
- **ext in a separate field** — `{"name":"x", "ext":"php"}` — the check
  may read `name` while the store appends `ext`
- **b64 decode paths** — invalid b64 (`!!!`), padding tricks (`=`, `==`),
  url-safe vs standard (`-_` vs `+/`), embedded whitespace/newlines —
  different decoders disagree on strictness
- **huge JSON** — `{"content":"<50MB b64>"}` — JSON-parser memory,
  body-size caps
- **type confusion** — `{"content": 123}` or `{"content": ["<b64>"]}` —
  coerced or crashed decoders
- **`format`/`mime` driving the decoder** — `{"format": "png", "content":
  <b64 of php>}` — check may trust `format` field
- **nested/base64-double** — b64 inside b64 — validators decode once

## The "the name is checked, the content isn't" pattern

```json
{"filename": "avatar.png", "content": "PD9waHAgcGhwaW5mbygpOyA/Pg=="}
```

Check sees `avatar.png` ext — store writes decoded `<?php phpinfo();?>`.
If the store reuses `filename` for the path, the file lands as `avatar.png`
— harmless ext. For exec you still need an exec-path — but now the
*content* is unfiltered, so a polyglot/second-order payload survives.

## `data:` URI specifics — the two-parser trick

```json
{"image": "data:image/png;base64,PD9waHAuLi4="}
{"image": "data:text/php;base64,..."}
{"image": "data:;name=x.php;base64,..."}
{"image": "data:image/svg+xml,<svg onload=.../>"}   — non-b64 data URI
{"image": "data:image/png;charset=x;base64,..."}
```

The `data:` mime claim vs the actual bytes — a validator may parse the
mime claim only. Also `data:` allows `;base64` ABSENT — raw percent-
encoded content — `data:image/svg+xml,%3Csvg...` delivers unencoded SVG.

## GraphQL uploads — the `graphql-multipart-request-spec`

```graphql
mutation($f: Upload!) { upload(file: $f) { id } }
variables: {"f": null}
operations: {"query":"mutation($f:Upload!){upload(file:$f){id}}","variables":{"f":null}}
map: {"0":["variables.f"]}
0: <file bytes>
```

It's multipart BUT the field names differ — a validator keyed on
`name="file"` misses `name="0"`. → `web-graphql` skill for the query side.

## Falsifiers

- the JSON path validates content strictly (real sniff) and the store is
  contained
- no JSON-upload endpoint exists — multipart only

## Output to record

- the field map (`filename`/`content`/`mime` equivalents)
- whether `filename`/store name and `mime`/check diverge
