# Predictable ids — when the generator is the bug

The id is high-entropy only if the source is. A time-seeded, sequential,
or name-derived id is recomputable.

---

## 1. The generator taxonomy

| Shape | Source | Predictable? |
|---|---|---|
| `42` | auto-increment | always |
| `1699999999` | epoch | within window |
| `uuid.v1()` | time+MAC | partially |
| `uuid.v3/v5()` | name hash | if name known |
| `ObjectId` | time+rand+counter | partially |
| `snowflake` | time+worker+seq | partially |
| `ulid` | time+random | partially |
| `hashids` | salt+int | if salt known |
| `md5(int)` | hash of int | recompute range |
| `sha1(email)` | hash of name | recompute |
| `b64(type:id)` | encoded composite | always |
| `str(random)` | CSPRNG | no |
| `secrets.token_*` | CSPRNG | no |

## 2. Sequential — the obvious

`1, 2, ..., N` — `id_sweep` covers it. The interesting ids:

```
id=0           — system/superuser/root
id=1           — admin/first-user
id=-1          — negative
id=2147483647  — int max
id=4294967295  — uint max
id=999999999   — large
id=1.0, "1", 01, 0x1, +1, 1e0  — coercion
```

`id=1` is almost always the admin. `id=0` may be a system account.

## 3. Time-derived — the window

`1699999999` (epoch) or `2024-11-05-0042` or `uuid v1` — the id embeds
creation time:

- You know the *target's* creation time (a registration response, a
  `created_at` field, a log timestamp) → brute the window around it.
- `id_sweep --range` covers a numeric timestamp range.
- uuid v1: the timestamp is 100-ns ticks since 1582 — a `created_at`
  gives the window; the `clock_seq`+`node` are the brute space.

```python
import uuid, datetime
# uuid v1 timestamp field
t = uuid.UUID('550e8400-e29b-11d4-...')
ts = (u.time - 0x01b21dd213814000) / 1e7  # epoch seconds
datetime.datetime.fromtimestamp(ts)
```

## 4. ObjectId — the timestamp prefix

`507f1f77bcf86cd799439011` — first 8 hex = epoch seconds:

- `created_at` leaks the timestamp → the first 8 chars are fixed.
- Brute the remaining 16 hex (5-byte random + 3-byte counter).
- `id_sweep` over the suffix space within a second window.

```python
import datetime
datetime.datetime.fromtimestamp(int('507f1f77',16))   # the creation time
# the last 16 hex are 5-byte random + 3-byte counter — brute within the window
```

## 5. Name-derived — recompute

`md5(email)` / `sha1(username)` / `md5(user_id)` / `uuid3(ns,name)` /
`uuid5(ns,name)` — if the id is a hash of a known name, recompute:

```python
import hashlib, uuid
# the id is md5(email)?
hashlib.md5(b"victim@t.tld").hexdigest()
# uuid5 of the name?
uuid.uuid5(uuid.NAMESPACE_DNS, "victim@t.tld")
# uuid3?
uuid.uuid3(uuid.NAMESPACE_DNS, "victim@t.tld")
# md5(int)?
for i in range(1,1000): hashlib.md5(str(i).encode()).hexdigest()
```

If you have a known email/username and the id is a deterministic hash,
the id space is recomputable.

## 6. hashids — the salt bug

`gY`, `jR`, `x5g` — hashids encodes ints with a salt:

```python
from hashids import Hashids
# default salt? empty? 'mysecret'? 'salt'? the app name?
for salt in ['', 'salt', 'secret', 'myapp', 'dev']:
    h = Hashids(salt=salt)
    try:
        print(salt, h.decode('gY'))
    except: pass
```

A default/empty/guessable salt → decode every id to its int → predict.

## 7. The PRNG-seeded id

`mt_rand()`/`rand()`/`Math.random()` — a non-CSPRNG:

- `mt_rand` seeded by time → recover the seed from one output → predict.
- `Math.random()` in JS → the seed is the xorshift state → recover.
- A `random.randint` in Python seeded by `time.time()` → recompute.

See `crypto-prng` for the state-recovery depth.

## 8. The composite-predictable

`tenant-7_doc-42` / `acme/inv/0042` — the composite has a predictable
part (`42`, `0042`) — sweep that part while holding the tenant.

## 9. The encoded composite — always predictable

`VXNlcjo0Mg==` = b64 `User:42` — the encoding is deterministic; the
int inside is sequential. Decode → change → encode. Always works.

## 10. The leak-source enumeration

When the id is opaque (real CSPRNG), you need a leak:

- `GET /api/users` — a list endpoint that dumps ids.
- `GET /api/users?limit=1000` — pagination dump.
- `GET /api/search?q=` — a search that returns ids.
- `GET /api/admin/users` — admin list.
- A Referer / Location / `Link:` header carrying an id.
- A public object's `owner` field carrying the owner's id.
- A GraphQL `users`/`nodes` query.
- A frontend bundle's hardcoded ids (`bundle_miner`).
- A source-map/source-repo's seed/fixture data.
- A shared/collaboration link (`?shared=ID`) — the id is the access.
- A "share" feature that generates the id — is the id predictable?

## 11. The "shareable link" id

`https://t.tld/shared/AbCdEf` — the sharing token. If it's:

- Sequential → sweep.
- A weak hash → recompute.
- A UUID v1 → predict from creation time.
- `b64(doc:id)` → decode.
- A real CSPRNG → needs a leak.

## 12. The type-juggling on the comparison

Even when the id is unpredictable, the *comparison* may be loose:

```
GET /files/{id} where the check is `file.owner == user_id`
id=0            → owner==0? (default column)
id=null         → owner==null? (unset column)
id=""           → owner==""? (empty default)
id=0.0          → loose-equal?
id="0"          → loose-equal?
id=false        → owner==false?
id=[]           → owner==[]?
id={}           → owner=={}?
id={"$ne":1}    → operator → owner!=1? (NoSQL)
id={"$gt":0}    → owner>0?
id={"$exists":true} → owner set?
```

The comparison operator is the second bug — see `web-nosqli` for the
operator surface.

## 13. The "the id IS the object" edge

Sometimes the "id" is the whole object path — `?file=doc42.pdf` — where
the predictable part is the number inside the filename. `file-idor.md`
covers the filename surface.

## 14. The sampling oracle

You can't enumerate a CSPRNG space — but you can verify *one* guess:

- `GET /files/{guessed-id}` → 404 vs 403. A 403 means the id exists but
  is forbidden — an existence oracle for ids.
- `id_sweep --hit-regex` catches a `200` hit.

## 15. The collision-birthday edge

A 4-hex-char id (`a1b2`) = 65536 space — enumerable. A 6-char alnum =
62^6 — enumerable-ish. An 8-char = 62^8 — too big. The space size is
the bound — `id_sweep` only works on enumerable spaces.

## 16. The deterministic-generation falsifier

The id is `secrets.token_urlsafe(32)` / `crypto.randomBytes` / `uuid4()`
— 128+ bits of real CSPRNG. Prediction is dead; the attack surface is
a *leak* (list endpoint, referer, log, GraphQL). Record the negative —
prediction closed, look for the leak.
