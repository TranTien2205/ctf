# Framework Sinks — where each framework hides the deserializer

## The point — the framework decides where the blob lives

Every framework has a canonical place it deserializes — the session cookie,
the cache, the job queue, a signed token. Find the framework first → its
canonical sink is where the blob is.

## The framework → sink map

| Framework | The canonical sink | The blob shape |
|---|---|---|
| Flask | `session` cookie | itsdangerous-signed (pickle pre-1.0, JSON post) |
| Django | `sessionid` / `Signer` | signed session/cookie |
| Rails | `_app_session` cookie / cache / job | Marshal under secret_key_base HMAC |
| Laravel | `XSRF-TOKEN`/`laravel_session` / queue | AES+HMAC serialized |
| Express | custom cookie / body | node-serialize / plain JSON |
| Spring | session/body/JMS | Java OIS |
| ASP.NET | `__VIEWSTATE`/`__EVENTVALIDATION` | LosFormatter + machineKey |
| Struts | OGNL/REST/XStream | XML deser |
| Symfony | session/cache | PHP serialize |
| WordPress | usermeta/options/transient | PHP serialize in DB |
| Joomla | session | PHP serialize |
| Drupal | cache/form_state | PHP serialize |
| Magento | session/quote | PHP serialize |

## The "the framework signs it" default

- **Rails** — `secret_key_base` HMAC over Marshal → key-attack
- **Laravel** — `APP_KEY` AES+HMAC → decrypt+re-encrypt
- **Django** — `SECRET_KEY` signer → forge with the key
- **Flask** — `SECRET_KEY` itsdangerous → forge with the key
- **ASP.NET** — `machineKey` MAC/encrypt → the key hunt
- **Express** — `secret` HMAC → forge
- **JWT** — `secret`/private key → alg attacks

## Per-framework details

### Flask

```
session = base64(zlib(json)).timestamp.sig     — modern, JSON
session = base64(pickle).timestamp.sig         — legacy (pre-1.0 itsdangerous default)
```

`SECRET_KEY` → `itsdangerous.URLSafeTimedSerializer(key).loads/dumps` —
forge a session object. If the serializer is the OLD pickle default — a
pickle gadget inside.

### Django

```
sessionid = b64(zlib(pickle|json)).sig          — signer wraps the value
```

Old `PickleSerializer` — pickle inside; the default is `JSONSerializer` since
1.6. A `SESSION_SERIALIZER=PickleSerializer` in settings.py = pickle sink.

### Rails

```
_app_session = b64(marshal).hmac                — Marshal + HMAC-SHA1
```

`secret_key_base` → Marshal payload inside the verified envelope. Older
`secret_token` (Rails 3) similar but different derivation.

### Laravel

```
laravel_session = base64(encrypt(serialized))   — AES-CBC+HMAC
XSRF-TOKEN = encrypted
```

`APP_KEY` (base64'd) → decrypt with `openssl`/framework encryptor →
serialize inside → re-encrypt. `phpggc` doesn't wrap the cookie — you wrap
with the framework's encryptor.

### Express/Node

```
session = b64(json).sig          — express-session HMAC
custom cookie = node-serialize   — $$ND_FUNC$$ the revive
```

`secret` → express-session forge; `node-serialize`/`funcster` for the
revive bug (the cookie is JSON-looking but carries functions).

### Spring/Java

```
session = serialized bean (rO0AB)
POST body = raw aced stream
JMS/Kafka = ObjectMessage body
```

The blob is `aced`/`rO0AB` — `java-deser.md`/`java-gadgets.md` for the
chain pick by the classpath.

### ASP.NET

```
__VIEWSTATE/__EVENTVALIDATION = LosFormatter + machineKey
auth cookie = forms-auth encrypt
```

`machineKey` → ysoserial.net `-p ViewState` — `dotnet-viewstate.md`.

### Struts

```
OGNL in a param + XStream REST deser
```

Struts2 CVE families — `XmlXStream`/`OGNL` params. The deser is in the
REST plugin's XStream or a parameter-coercion path.

### Symfony

```
session/cache = PHP serialize
a signed _token = HMAC
```

Symfony's serializer/deserializer on typed values + `unserialize` on
session/cache — `php-deser.md` chains on Symfony libs.

### WordPress/Joomla/Drupal/Magento — the PHP CMS family

- **WordPress**: `unserialize` on usermeta/options/transient — a writeable
  meta key is the sink; plugins add their own
- **Joomla**: session unserialize — CVE-2020-35749 family
- **Drupal**: cache/form_state unserialize + `phar` via PEAR_ArchiveTar
- **Magento**: session/quote unserialize — CVE-2016-4010/2018-10561

## The lockfile → version → gadget recipe

```bash
# the lockfile is the version oracle:
cat composer.lock | python3 -c "import json,sys;[print(p['name'],p['version']) for p in json.load(sys.stdin)['packages']]"
cat package-lock.json | python3 -c "import json,sys;[print(k,v['version']) for k,v in json.load(sys.stdin).get('dependencies',{}).items()]"
cat Gemfile.lock
cat pom.xml | grep -A2 artifactId
# → the version picks the phpgcc/ysoserial chain or the CVE
```

## The "framework didn't sign it" gaps

- a cookie the app signs with a DIFFERENT key (`secret` vs `secret_key_base`)
- a second-order store (session/cache/db/job) that isn't the signed cookie
- a field inside the signed envelope that isn't itself checked
- an `alg=none`/`kid`/`confusion` path on a JWT-wrapped blob
- a custom serialize call the framework doesn't wrap (a `unserialize` on a
  body field, not the session cookie)

## Falsifiers

- `safe_load`/`allowed_classes`/`Binder`/`JSONSerializer` verified + key
  unreachable → closed for that channel
- the framework's canonical sink is the ONLY deser point AND it's
  JSONSerializer/safe — then the app's own `unserialize` on a body field
  is the remaining surface (second-order or an explicit endpoint)

## Output to record

- The framework + its canonical sink + the wrapping (sign/encrypt)
- The version the lockfile pins + the chain that covers it
- The verbatim response/OOB proving the chain fired
