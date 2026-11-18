# Format Signals — the request-shape tells before the blob is decoded

## The point — the request shape predicts the format before decoding

A challenge that never shows you a blob still leaks the format — headers,
field names, page type, framework fingerprint. This is the "predict the
format from the envelope" card.

## The request-shape → format map

| Observable | Format likely |
|---|---|
| `Content-Type: application/x-java-serialized-object` | Java OIS |
| `Content-Type: application/octet-stream` + b64 blob | binary format inside b64 |
| `Content-Type: text/xml` / SOAP envelope | XStream/XMLDecoder/SoapFormatter |
| `Content-Type: application/x-yaml` / `.yml`/`yaml` | PyYAML/Snakeyaml/Psych |
| `{"$type":`/`{"__type":`/`{"@type":` | Json.NET/JavaScriptSerializer/fastjson |
| `__VIEWSTATE`/`__EVENTVALIDATION` | LosFormatter |
| `Accept: application/x-java-serialized` | Java OIS |
| `X-Java-Serialized-Object`/`X-Serialized` | Java OIS |
| `Set-Cookie: ..._session=`/`laravel_session`/`sessionid` | framework-wrapped serialize |
| a `.aspx`/`.ashx`/`.asmx` endpoint | ASP.NET — ViewState |
| a `.jsp`/`.do`/`.action` endpoint | Java — OIS/Struts |
| `X-Powered-By: PHP` | PHP serialize |
| `X-Powered-By: Express`/`X-Runtime: 0.0` | Node — node-serialize/JSON |
| `Server: Werkzeug`/`gunicorn`/`uvicorn` | Python — pickle/PyYAML |
| `Server: Ruby`/`X-Powered-By: Phusion` | Ruby — Marshal/Psych |
| `JBoss`/`WebLogic`/`WebSphere`/`Tomcat` | Java OIS |
| `phpmyadmin`/`wordpress`/`drupal`/`magento`/`joomla` | PHP serialize in CMS |
| `Laravel`/`Symfony`/`Yii`/`CodeIgniter` | PHP serialize in framework |
| `Spring`/`Django`/`Flask`/`Rails` | framework session |

## The field-name tell — the param that names itself

```
data, obj, object, blob, payload, state, session, user, prefs, data_64,
serialized, bean, dto, model, viewstate, __VIEWSTATE, dataObject,
javaobject, serializedobject, content, import, backup, restore, job, task,
queue, msg, message, body, raw, bin, ser
```

A field named `serialized`/`viewstate`/`dataObject`/`import` is a scream —
the name is the format's name.

## The endpoint-name tell

```
/import, /upload, /backup, /restore, /sync, /task, /job, /queue, /msg,
/api/deserialize, /api/unmarshal, /api/load, /api/parse, /api/read,
/api/import, /api/object, /ws/..., /jms/..., /rpc/...
```

`/import`/`/upload`/`/restore`/`/api/object` — the endpoint's name is the
deserializer's purpose.

## The framework → format shortcut — the whole cheat

```
Rails          → Marshal / Psych
Django/Flask   → pickle / JSON / PyYAML
Express/Node   → node-serialize / JSON / js-yaml
Laravel/Symfony→ PHP serialize
WordPress      → PHP serialize (usermeta/options)
ASP.NET        → BinaryFormatter/ViewState/Json.NET
Struts         → XStream/OGNL
Spring         → Java OIS
JBoss/WebLogic → Java OIS / T3
Tomcat         → Java OIS
```

## The "stack says which" chain

```
headers say PHP        → look for O:/a:/s: blobs  → php-deser.md
headers say IIS        → look for __VIEWSTATE/AAEAAAD → dotnet-deser.md
headers say Tomcat     → look for rO0AB/aced → java-deser.md
headers say Rails      → look for BAh / _session → ruby-deser.md
headers say Flask      → look for eyJ / gAN → python-deser.md
headers say Express    → look for _$$ND_FUNC$$_ → nodejs-deser.md
the body is YAML       → look for !!/!ruby/ → yaml-deser.md
the body is XML        → look for <com.x> → other-formats.md
```

## The "is it really serialized" filter — when it's just JSON

- `{"a":1,"b":[2]}` — plain JSON → `JSON.parse` → NOT deser
- `eyJ...` JWT — the payload is JSON → JWT/auth-session, not deser
- `name=value&x=y` — form data → not deser
- a b64 blob that decodes to `{"x":1}` — JSON → not deser
- a b64 blob that decodes to `O:`/`aced`/`gAN`/`BAh`/`AAEAAD` → DESER

The decode is the discriminator — the request shape predicts, the magic
bytes confirm.

## Output to record

- The request-shape tell that pointed at the format
- Whether the decode confirmed it
- Which module the fingerprint routes to
