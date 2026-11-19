# Detection checklist deep — each detection step with the response-reading rules

`detection-checklist.md` is the printable sequence. This module adds
the response-reading per step — what each result means and the next
move it selects.

## Step 1 — the register body

```
POST /register {..., "role":"admin"} → GET the object
```

| Read-back | Meaning | Next |
|---|---|---|
| `role:admin` | binder merges extras | CONFIRM → enumerate role reach |
| `role:user` | allowlist | nested/array/content-type paths (1 probe each) |
| `400 unknown field` | strict schema | other content-types |
| `201` + echo `role:admin`, read-back `role:user` | echo artifact | the read-back decides — falsifier |

## Step 2 — the workflow endpoints

```
POST /confirm orderId=1 (no /pay)
```

| Response | Meaning | Next |
|---|---|---|
| `200` + `confirmed, paid:false` | precondition unchecked | CONFIRM → flag field |
| `302`/`400` earlier step | state enforced | locate the state carrier |
| `200` + `status:pending` | soft no-op | negative — unchanged state |
| `404` | object-scoped check | mint a fresh cart first |

## Step 3 — arithmetic endpoints

```
POST /cart qty=<boundary>
```

| Response | Meaning | Next |
|---|---|---|
| `400` | validator | next FIELD |
| `200` + `total:-50` | sign unchecked | CONFIRM → checkout |
| `200` + `qty:0` | clamped | note the clamp layer |
| `200` + `total:NaN` | NaN propagated | CONFIRM → checkout |
| `500` | unguarded arithmetic | CONFIRM different-layer |

## Step 4 — replay endpoints

```
POST /redeem ×2
```

| Result | Meaning | Next |
|---|---|---|
| `+50` twice | no marker | CONFIRM |
| `409` second | endpoint dedup | key-scope probes |
| `200` twice `+50` once | ledger dedup | ledger key coverage |

## Step 5 — transform endpoints

```
id=<limit> vs id=<limit+1> vs id=<malformed>
```

| Rejection | Meaning | Next |
|---|---|---|
| limit+1 ≠ malformed shape | transform ran unchecked | CONFIRM → wrap math |
| identical | check covers transform | falsifier — other transforms? |

## Step 6 — trust endpoints

```
step1 mints {"price":50} → step3 send {"price":1}
```

| Result | Meaning | Next |
|---|---|---|
| `charged:1` | trusted | CONFIRM |
| `400 mismatch` | recomputed | falsifier — OTHER carried values |

## The reading rules

1. **Every 200 needs a read-back** — the write's response is the echo;
   the GET is the store.
2. **Every rejection names a layer** — status+text+timing buckets map
   the rejection stack.
3. **Every confirm needs its baseline** — the pair is the evidence.
4. **Every falsifier names its depth** — endpoint / binder / model /
   mechanism — so the next probe knows what remains open.
