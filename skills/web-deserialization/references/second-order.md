# Second-Order Deserialization — stored objects that fire later

## The shape

```
write path:   POST /profile   → stores a value into session/cache/job/db
read path:    later — a different request (or a background job) unserializes
              the stored value → the gadget fires OUT OF BAND
```

The payload never passes through the request that triggers it — it sits in
the store until a consumer unserializes. The response to the WRITE is clean;
the response to the later READ (or a callback) carries the evidence.

## Where the store is

| Store | Write vector | Read/trigger vector |
|---|---|---|
| session file/redis | any endpoint writing `$_SESSION` | next request that starts session / an admin view |
| DB column | a profile/pref field | a different endpoint that reads+unserializes the row |
| cache (memcached/redis) | a `set`/`put` endpoint | another endpoint's `get`/`fetch` |
| job queue | enqueue endpoint | the worker that dequeues+loads |
| file on disk | upload/backup | a background import/cron |
| cookie jar state | one response sets it | a later request reads it |

## The trigger pattern — find the consumer

The write is useless without a read. In source, find the pair:

```php
// write:    $_SESSION['prefs'] = $_POST['prefs'];       (stores raw)
// trigger:  $u = unserialize($_SESSION['prefs']);       (fires later)
```

```java
// write:    cache.put("k", value)
// trigger:  Object o = ois.readObject(cache.get("k"))
```

```python
# write:    redis.set('job:'+id, pickle.dumps(x))
# trigger:  worker → pickle.loads(redis.get(k))
```

## The OOB confirm — because the firing is out of band

The response to the trigger request may not show the RCE output (the chain
ran in a worker/cron/another process). Confirm by side channel:

- **URLDNS/JNDI/`nslookup` gadget** — the callback fires when the stored
  object is deserialized, no matter which process runs it
- **file write gadget** — write a marker to a path you can later read
- **`time`/`sleep` gadget** — a measurable delay on the trigger request
- **SoapClient/JNDI URL fetch** — OOB HTTP hit

## The write path doesn't need a signature

A second-order sink often skips the signature check — the *stored* value is
trusted because "the server wrote it". If you can write into the store via a
legitimate endpoint (profile update, a `put` API, an enqueue), the signature
that protects the direct channel doesn't protect this one — the value is
signed at WRITE time by the app, then unserialized at READ time on the same
bytes you supplied.

## Hunting the pair

```bash
# grep for write-then-read patterns:
grep -rn "unserialize\|readObject\|pickle.loads\|Marshal.load" --include='*.php' --include='*.java' --include='*.py' .
# → for each unserialize call site, trace back where its argument came from

# session/cache/job stores:
grep -rn "session\|cache\.\|redis\|memcache\|queue\|enqueue" .
```

## The classic CTF shapes

- **Registration + profile read**: register with a serialized blob in a
  field → an admin/report endpoint reads the row through `unserialize`.
- **Cache warm/poison**: a `PUT /cache/k` writes bytes, a `GET /cache/k`
  unserializes.
- **Job queue**: enqueue a `pickle`d/serialized job → worker runs it.
- **Avatar/import**: upload a serialized file → a background reprocess
  unserializes.
- **Multi-step form**: step-1 stores your serialized blob, step-3 loads it.
- **A "preview" endpoint** that re-reads what you just saved.

## Falsifiers

- The store round-trips verbatim (stored→returned) without a deserializer
  on the read path → inert storage.
- The value is re-serialized at write time (JSON→PHP serialize→store) —
  your bytes never reach the grammar.
- Every read path `safe_load`s/`allowed_classes=>false` → dead.
- No writeable endpoint reaches the store at all.

## Output to record

- The write endpoint + the read/trigger endpoint (the PAIR)
- The store it lives in (session/cache/db/job/file)
- The OOB evidence the stored object fired
