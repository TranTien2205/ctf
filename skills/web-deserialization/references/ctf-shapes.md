# CTF Shapes — how deserialization challenges actually look

## The five delivery shapes

### 1. The cookie — the most common

A session/`remember_me`/`user`/`prefs` cookie carrying a signed or unsigned
serialized blob. Fingerprint the bytes → pick the format module.

```
Flask:   session=eyJ...   (JSON post-1.0, itsdangerous-pickle pre-1.0)
Django:  sessionid=...    (signed — old pickle serializer vs JSON)
Rails:   _app_session=... (HMAC + Marshal)
PHP:     custom cookie = base64(serialize(...))
Java:    a serialized bean in a cookie
ASP.NET: __VIEWSTATE + auth cookie
```

**The challenge shape**: "the key is in `.env`/`config.py`/`secrets.yml`/
`web.config`" or "the cookie is unsigned" or "alg=none accepted".

### 2. The API body field

```json
{"data":"<b64 blob>"}
{"obj":"O:8:\"User\":..."}
{"@type":"com.sun.rowset.JdbcRowSetImpl",...}
POST /import  application/octet-stream → raw AC ED
```

A JSON/XML/binary body field unmarshalled by the endpoint. Common on
`/api/import`, `/api/user`, `/api/sync`, `/api/task`.

### 3. The file the app unmarshals

- upload a `.ser`/`.pkl`/`.bin`/`.npy`/`.joblib` the app `load`s
- a `config.yml`/`backup.yml` the app `yaml.load`s
- a `.phar` uploaded as `.jpg` + a `phar://` file-op trigger
- an `import.xml` → XMLDecoder/XStream
- a `.npy` with `allow_pickle=True` in an ML challenge

### 4. The hidden parameter

A hidden form field, a `ViewState`, a `data`/`state`/`obj`/`blob`/`payload`
URL param, a `X-Custom-Data` header. The blob is the field's VALUE — decode,
fingerprint, gadget.

### 5. The second-order store

Session/cache/job/db write on one endpoint → deserialize on another. See
`second-order.md`.

## The challenge-signal → format map

| Observable | Likely format |
|---|---|
| `Set-Cookie: session=eyJ...` + `Flask`/`Werkzeug` header | itsdangerous JSON (post-1.0) or signed pickle (pre-1.0) |
| `Set-Cookie: _app_session=` + `X-Powered-By: Phusion`/`Ruby` | Rails Marshal under HMAC |
| `__VIEWSTATE` + `.aspx` | LosFormatter + machineKey |
| `rO0AB`/`aced0005` body + `tomcat`/`jetty`/`jboss` | Java OIS |
| `O:\d+:"`/`a:\d+:{` + `PHP`/`X-Powered-By: PHP` | PHP serialize |
| `gAN`/`gAR`/`gAQ` base64 + `python`/`flask`/`django` | pickle |
| `BAhJ`/`BAh` base64 + `ruby`/`rails` | Marshal 4.8 |
| `AAEAAAD`/`__VIEWSTATE` + `IIS`/`ASP.NET` | BinaryFormatter/LosFormatter |
| `{"$type":`/`{"__type":` body + `.NET`/`Newtonsoft` | Json.NET/JavaScriptSerializer |
| `_$$ND_FUNC$$_`/`!!js/function` + `node`/`express` | node-serialize/js-yaml |
| `!!python/`/`!ruby/`/`!!javax` in a YAML body | PyYAML/Psych/Snakeyaml |
| `.pkl`/`.npy`/`.joblib` upload | pickle/numpy/joblib |

## White-box signature — the source grep

```bash
# the sink calls — find them first:
grep -rn "unserialize\|readObject\|pickle.loads\|Marshal.load\|yaml.load\|BinaryFormatter\|JsonConvert.Deserialize\|XMLDecoder\|XStream\|unserialize\|loads(\|fastjson\|ObjectInputStream" --include='*.php' --include='*.java' --include='*.py' --include='*.cs' --include='*.js' --include='*.rb' .

# the wrapper — what signs/unwraps the blob before the sink:
grep -rn "base64\|decrypt\|verify\|signature\|hmac\|itsdangerous\|MessageVerifier" .
```

## The challenge-title tells

- "Session", "Cookie", "RememberMe" → cookie shape, look for the key
- "Import", "Upload", "Backup", "Restore" → file-unmarshal shape
- "Queue", "Job", "Task", "Worker" → job-queue second-order
- "Cache", "Store" → cache-poison second-order
- "Legacy", "Java", "Admin" → Java OIS
- "Pickle", "Py", "Snake" → pickle
- "View", "Aspx", "DotNet" → ViewState

## The "is the flag the RCE or a file" question

Deserialization challenges almost always end in one of:

- `os.system('cat /flag')` / `Process.Start` → flag in the response/OOB
- file-read gadget (`open('/flag').read()`) → flag in the value reflected
- `__toString`/`toString` returning `/flag` contents → flag in the render
- a `Runtime.exec` callback URL embedding the flag

The flag is usually at `/flag`, `/flag.txt`, `flag.txt` in webroot, the app
root, an env var `FLAG`, or a DB row the chain queries.

## Falsifier — when it's NOT deserialization

- The blob is `eyJ...` JSON inside a JWT — the bug is JWT, not deser.
- The "serialized" field is stored verbatim and never `loads`/`unserialize`d.
- The app uses `safe_load`/`allowed_classes=false`/`TypeNameHandling.None`
  AND no gadget-reachable permitted class.
- The blob is encrypted (not just signed) with an unreachable key AND no
  padding-oracle/decrypt path.

## Output to record

- The delivery shape (cookie/body/file/param/store) + the format
- Whether a signature/key was involved and how it was reached
- The verbatim flag-bearing response
