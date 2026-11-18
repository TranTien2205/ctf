# Form-Field Confusion — the file that lands in a text field

## The shape — file content submitted where a string is expected

```
name="username" — a filename
name="email"    — a filename containing a payload
name="avatar"   — file part
name="title"    — text field receiving file bytes
```

Field-confusion attacks place the file's bytes or its NAME into a field
the server processes as text — `filename-injection.md`'s cousin.

## The "filename in a text field" — name-as-string injection

`name="email"` receives `x.php` — the server stores `x.php` as the
"email" field — if that field is later used in a query/template/log —
the name is the injection:

- `x.php` → stored as a "filename" field → when displayed → XSS
- `'; DROP TABLE` → SQLi via the field
- `{{7*7}}` → SSTI
- `$(id)` → cmdi

The upload handler's `filename` param is just another string field —
test it for every injection class — `filename-injection.md`.

## The "the file landed in the wrong field" — field-name collisions

Two parts, same `name=`:

```
name="avatar" — real file
name="avatar" — attacker-controlled text/string field
```

PHP `$_FILES['avatar']` vs `$_POST['avatar']` — which one the handler
uses decides the check. The string-version may skip the file-type check.

## `name` vs `filename` in Content-Disposition — the two names

```
Content-Disposition: form-data; name="avatar"; filename="x.php"
```

`name` is the field; `filename` is the file — some handlers use `name`
for the check, `filename` for the write — sending `filename=` without
`name` or vice versa — which does the app actually key on?

`filename=` empty (`filename=""`) — some handlers treat it as a text
field not a file — the content lands in `$_POST` not `$_FILES`.

## The `name[]` array trick

`name="avatar[]"` vs `name="avatar"` — array-vs-scalar confusion:

- `avatar[]` makes `$_FILES`/`$_POST` an array — a scalar check on
  `$_POST['avatar']` gets an array — type-confusion
- `avatar[x]` — nested key — `$_POST['avatar']['x']` — parameter pollution

## The field-order game — which part wins

```
name="x" type=text: "safe"
name="x" type=file: <binary>
```

or two `name=` parts with the same name — PHP's last-wins; some
frameworks take the first; some merge to arrays — the order decides
which value the check sees.

## The "a file body in a query param" — url-param carrying bytes

`?avatar=<file-bytes>` or `?data=<b64>` — the upload isn't a multipart
at all — the param gets stored as a file — `json-upload-apis.md`'s
base64-body variant.

## Detection — which fields does the handler actually read?

- white-box: the handler's field names — `$_FILES['x']`, `req.files.y`,
  `request.FILES['z']` — test those names exactly
- black-box: swap `name=` values in parts, observe which writes

## Falsifiers

- the handler only processes the documented file field, and name/filename
  handling is consistent
- field-level injection into `filename=` is escaped on every sink

## Output to record

- which `name=` the handler reads + whether `filename`/`name`/array
  confusion changes the validation applied
