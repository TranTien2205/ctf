# Sequential enumeration — the id space is ordered

The id is an auto-increment / timestamp / counter — the space is
predictable and enumerable.

---

## 1. The format

- **Auto-increment**: `1,2,3,...,42,...,N` — the database's `AUTO_INCREMENT`
  or `SERIAL`.
- **Timestamped**: `1699999999` (epoch), `20240101120000` (datetime), a
  monotonic sequence.
- **Offset**: `id = base + user_offset` — `user_id = 1000 + n`.
- **Composite**: `order_0042`, `invoice_0042`, `user-42` — the numeric
  part is sequential inside a prefix.
- **Padded**: `0001`, `0042`, `00042` — zero-padded counter.
- **Gap-filling**: `1,2,3,...` but with deleted gaps — `4,7,9` exist.

## 2. The oracle — existence

```bash
python3 tools/web/id_sweep.py --url "$BASE/api/notes/{id}" \
  --header "Cookie: session=$B" --range 1-500 \
  --hit-regex '"id"\s*:\s*\d+|"text"' --miss-regex '404|"error"|"not found"' \
  --rate 10 --limit 500
```

The `id_sweep` walks the range — `--hit-regex` on a field that exists
only for a real object, `--miss-regex` on the `404`/`error` shape.

## 3. The oracle — ownership

The sweep's `--hit-regex` should be *attributable* — `"owner_id":1` /
`"email":"a@"` / `"created_by":1` — so a hit is an object *not B's*,
not just "an object".

```bash
python3 tools/web/id_sweep.py --url "$BASE/api/notes/{id}" \
  --header "Cookie: session=$B" --range 1-500 \
  --hit-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@' \
  --miss-regex '404|"error"|"not found"|"owner_id"\s*:\s*2' \
  --rate 10 --limit 500
```

## 4. The "the first is admin" shape

`id=1` — the auto-increment's first row is the seeded admin/test user.
`GET /users/1` is the single most common IDOR-CTF win. Try `id=0`,
`id=1`, `id=-1`, `id=2` first — before the sweep.

## 5. The "the adjacent" probe

You own `id=42` — `id=41`/`id=43`/`id=1`/`id=9999`. Adjacent first
(the one request `pre-probe` allows cheap), then the structured sweep.

## 6. The "the timestamp" shape

`id = created_at` epoch — `1699999999`. The space is bounded by the
app's lifetime. `created_at` from `GET /me` tells you your own epoch —
the neighbors are other users.

## 7. The "the padded" shape

`invoice_0042` — the zero-pad is part of the format; `id_sweep` with
`--mutate 'str(i).zfill(4)'` or a wordlist `0001-0500`.

## 8. The "the prefixed" shape

`order_0042` / `user-42` / `ORD-00042` — the id is `{prefix}-{num}`.
`--mutate 'f"order_{i:04d}"'` or a wordlist.

## 9. The "the composite" shape

`user:42:token` / `42.v1` / `42+abc` — the numeric part is inside a
composite. The `--mutate` rebuilds it per `i`.

## 10. The "the gap" oracle

`id=4` returns `200`, `id=5` returns `404`, `id=6` returns `200` — the
`200`/`404` is the existence oracle (which ids are live). The `200`
carrying `owner_id:1` is the ownership oracle.

## 11. The "the soft-deleted" shape

`id=4` was deleted — `GET` returns `404` but `?include_deleted=true`/
`/trash/4`/`?deleted=true` returns it.

## 12. The "the range bounds"

`id_sweep --range 1-100` for the near space; `--range 1-1000` wider.
The budget is the bound — don't sweep the whole int space; sweep where
the app has objects.

## 13. The "the header also" shape

The id is in a header — `X-User-Id: {id}` — `id_sweep --header
'X-User-Id: {id}'` sweeps it as a header.

## 14. The "the body also" shape

`POST /api/data {"id":{id}}` — `id_sweep --method POST --body
'{"id":{id}}'` sweeps the body field.

## 15. The "the format-string" shape

`user_42` → the `--mutate` builds `f"user_{i}"`; `42:user` → `f"{i}:user"`.
The `--mutate` is the arbitrary rebuild.

## 16. The "the rate"

`--rate 10` — 10 req/s on a shared instance. The budget is the bound;
a `429` means the rate is too high.

## 17. The "the stop-on-flag"

`--stop-on-flag` — stop the sweep the moment a flag-shaped hit lands;
the flag is the target, not the count.

## 18. The "the bulk-carrier" shape

`GET /users?ids={id}` — `id_sweep --url '...?ids={id}'` sweeps the
bulk param one id at a time.

## 19. The "the out" artifact

`--out hits.json` — the sweep's hits land in a file for review; the
`--response` for `post-probe` is the hit's body.

## 20. The falsifier

`id_sweep` over the range → no `hit` beyond B's own → the check is
uniform. Record `refutes` on the sweep result.
