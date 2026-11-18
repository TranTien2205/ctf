# Identifier formats — every id shape, and how each is attacked

The format determines the attack. A sequential int is swept; a UUID v1 is
predicted; a hash is either recomputable or not.

---

## 1. Sequential integer

`1, 2, 3, ..., 42, ..., 1003` — auto-increment.

- Attack: `id_sweep` over the range, or step ±1 from a known id.
- `id=0`, `id=-1`, `id=1.0`, `id=1e0`, `id=01`, `id=+1` — coercion.
- `id=1003` vs `id=1003.0` vs `id="1003"` — type juggling.
- The first id (`1`) is usually admin/system — probe it.

```bash
python3 tools/web/id_sweep.py --url "$BASE/api/users/{id}" \
  --header "Cookie: session=$B" --range 1-100 \
  --hit-regex '"role"\s*:\s*"admin"|"email"' --miss-regex '404|"error"'
```

## 2. UUID

`550e8400-e29b-11d4-a716-446655440000` — the version digit at position 13.

- **v1** (time+MAC): `xxxxxxxx-xxxx-1xxx-...` — predictable from timestamp
  + node. See `uuid-analysis.md`.
- **v2** (DCE): rarely seen.
- **v3/v5** (name-based MD5/SHA1): recomputable from the namespace+name —
  `uuid.uuid3(ns, "42")`. If you know the name, you recompute.
- **v4** (random): NOT predictable — needs a leak.
- **v6/v7** (time-ordered): the timestamp is embedded → brute-force the
  counter within a window.
- **nil UUID** `00000000-0000-0000-0000-000000000000` — a default that
  may bind to a system object.
- **max UUID** `ffffffff-ffff-ffff-ffff-ffffffffffff`.

```python
import uuid
# recompute v3/v5 if you know the namespace + name
uuid.uuid5(uuid.NAMESPACE_DNS, "user:42")
uuid.uuid3(uuid.NAMESPACE_DNS, "admin")
# decode v1 timestamp
u = uuid.UUID('...')
u.time  # 100-ns intervals since 1582-10-15
```

## 3. MongoDB ObjectId

`507f1f77bcf86cd799439011` — 24 hex chars = 4-byte timestamp + 5-byte
random + 3-byte counter.

- The first 8 hex chars are the **creation timestamp** — sortable.
- Two ObjectIds created in the same second share the first 8 chars —
  brute-force the last 16 (random+counter) within a window.
- A timestamp-only ObjectId (`507f1f770000000000000000`) is the
  "first object at that time" — a range bound.

```python
# ObjectId -> datetime
import datetime
datetime.datetime.fromtimestamp(int('507f1f77',16))
# brute-force the last 16 hex within a second window
```

## 4. Snowflake / Twitter id

`1234567890123456789` — timestamp + worker + sequence. Time-ordered.

- The high bits are the timestamp — a snowflake embeds creation time.
- Two ids created close together share the high bits — brute the sequence.

## 5. ULID

`01ARZ3NDEKTSV4RRFFQ69G5FAV` — Crockford base32, 48-bit time + 80-bit
random. Time-ordered, sortable.

- First 10 chars are the timestamp — brute the last 16 (random) within a
  window.

## 6. NanoID / cuid / ksuid

- `nanoid` — URL-safe random, NOT predictable (CSPRNG).
- `cuid` — timestamp+counter+random — partially predictable.
- `ksuid` — timestamp+random — time-ordered, brute the random part.

## 7. Hashids

`gY` / `jR` / `x5g` — a hashid encodes an integer with a salt. If the
salt is weak/default, decode it back to the int.

```python
# hashids — decode if salt known/guessable
from hashids import Hashids
h = Hashids(salt='')
h.decode('gY')  # -> (42,)
```

- The salt is often in source/config — a leaked salt → decode all ids.

## 8. Base64-encoded id

`dGVzdA==` / `VXNlcjo0Mg==` — b64 of `test` or `User:42` (Relay global id).

- Decode it — it may be a composite `Type:id`.
- `VXNlcjo0Mg==` → `User:42` — the Relay/GraphQL node id. Change `42`.

```bash
echo 'VXNlcjo0Mg==' | base64 -d   # User:42
echo 'VXNlcjox' | base64           # -> VXNlcjox (User:1)
```

## 9. Hex-encoded id

`6131613031` — hex of `a1a01`. Decode → may be an int or a string.

## 10. Composite id

`user:42` / `tenant-7_doc-42` / `acme/inv/0042` — a composite of parts.

- Change one part — the `42` while keeping `tenant-7` → cross-tenant.
- `acme/inv/0042` → `acme/inv/0001` or `other/inv/0042`.

## 11. Slug

`/posts/hello-world` — a slug. `?slug=admin-post` or the numeric id
behind it (`/posts?slug=x` vs `/posts?id=42`).

- Try the numeric equivalent — `/posts/hello-world` may also be
  `/posts/42`.
- `?slug=` may accept traversal (`../admin/secret`).

## 12. Filename-as-id

`?file=report_2024_42.pdf` — a filename. `?file=../../etc/passwd` —
traversal. `?file=report_2024_41.pdf` — adjacent. `?file=report_ADMIN.pdf`
— a named file. See `file-idor.md`.

## 13. Encrypted/signed id

`eyJhbGciOi...` (a JWT) or `gAAAAABh...` (Fernet) or a signed blob —

- If it's a signed opaque blob, the signature is the gate — see
  `web-auth-session` (forge needs the key).
- If it's *encrypted* not signed — bit-flip or padding-oracle may apply.
- If it's `itsdangerous`/`Fernet` — `web-deserialization` covers it.

## 14. Hash-as-id (MD5/SHA1/SHA256)

`5f4dcc3b5aa765d61d8327deb882cf99` — `md5("password")` or `md5(42)`.

- If the id is `md5(int)` — recompute `md5(i)` for the range → predict.
- If it's `sha1(email)` — recompute for a known email.
- If it's `md5(time)` — recompute for a timestamp window.
- If it's `hash(secret+int)` — needs the secret.

```python
import hashlib
for i in range(1,1000):
    print(i, hashlib.md5(str(i).encode()).hexdigest())
# match a leaked hash to recover the int
```

## 15. Sequential-with-offset

`100042, 100043, ...` — sequential with a fixed offset. Or `42*7919`
(prime-multiplied). Or `42^0xdead` (XOR). Identify the transform:

- Collect two consecutive ids — the delta is the offset/multiplier.
- `42` → `334038` (`42*7957`)? the multiplier is recoverable.
- XOR-masked: `42^mask` — collect two, XOR to recover mask.

## 16. Time-based id

`1699999999` (epoch) or `20241105-0042` (date+seq) or `42-1699999999`
(id+time).

- A timestamp id → predict for a creation window.
- `20241105-0042` → `20241105-0001` (earlier that day).

## 17. Random-string id (opaque)

`a8f3k2j9x1` — high-entropy CSPRNG. NOT predictable — needs a leak:
- An endpoint that lists ids.
- A Referer/log that carries it.
- A GraphQL `nodes`/`users` query that dumps ids.
- A `?page=`/`?offset=` enumeration that returns ids.

## 18. The "the id is the flag" edge

Sometimes the object id IS the flag — `/files/{flag}` — or the flag is
a field on the object the id addresses. The id is the reach; the flag is
behind it.

## 19. Format identification

```bash
# numeric?
[[ "$ID" =~ ^[0-9]+$ ]] && echo seq
# uuid?
[[ "$ID" =~ ^[0-9a-f-]{36}$ ]] && echo uuid
# mongo ObjectId (24 hex)?
[[ "$ID" =~ ^[0-9a-f]{24}$ ]] && echo objectid
# b64?
echo "$ID" | base64 -d 2>/dev/null && echo b64
# hex?
[[ "$ID" =~ ^[0-9a-f]+$ ]] && echo hex
# hash (32/40/64 hex)?
[[ "$ID" =~ ^[0-9a-f]{32}$ ]] && echo md5
[[ "$ID" =~ ^[0-9a-f]{40}$ ]] && echo sha1
[[ "$ID" =~ ^[0-9a-f]{64}$ ]] && echo sha256
```

## 20. The type-coercion attacks on every format

Whatever the format, try:

```
id=1        → id=1.0, id="1", id=+1, id=-1, id=01, id=1e0, id=0x1
id=abc      → id=ABC, id=Abc, id=abc , id= abc, id=abc%00, id=abc%20
id=42       → id=[42], id={"id":42}, id[]=42, id.0=42, id=42&id=43
uuid        → nil uuid, max uuid, uppercase, no-dashes, braces {uuid}
objectid    → timestamp-only (first-at-time), all-zero, all-f
```

A type-coerced id may bypass a loose check (`id == 1` matches `1`, `1.0`,
`"1"`, `01`, `0x1`, `1e0`, `+1`) while the strict-typed lookup misses.
