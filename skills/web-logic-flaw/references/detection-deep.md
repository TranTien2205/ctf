# Detection deep — reading the state machine out of the app

Detection for logic flaws is not "find the dangerous parameter" — it is
**reconstruct the implemented state machine** and find the edges the
imagined workflow lacks. This module is the deep read: where the state
machine hides and how to enumerate it.

## Where the state machine lives

### The endpoint list IS the edge list

Every state-changing endpoint is a transition. Enumerate them:

```bash
python3 tools/web/bundle_miner.py --url <bundle-url> --out /tmp/bundle
# /tmp/bundle/endpoints.txt — every path the front-end calls
```

Then sort them by what they mutate:

- **creation**: register, cart, order, session
- **transition**: pay, confirm, redeem, verify, cancel, refund, claim
- **terminal**: flag, download, admin, export

The bug candidates are the *transitions* — each one is a precondition to
test. For each transition endpoint ask: **what does it check?** The gap
between its check and the imagined workflow's requirement is the flaw.

### The response is a field map

`GET` responses enumerate the model's fields. `GET /api/user/me`
returning `{"role": "user", "balance": 0, "verified": false}` names every
mass-assignment target — those are the fields to send at `register`/`update`.

### The front-end is the spec

The bundle encodes the *imagined* workflow — the order the JS calls
endpoints is the line; the handlers' actual acceptance is the graph.
Where they diverge:

- JS calls `/pay` then `/confirm` — does `/confirm` work alone?
- JS sends `{"qty": 1}` — does the handler bound `qty` at all?
- JS reads `state` from a cookie — is that cookie the state machine's
  only record?

Pachinko's first step exactly: read the client bundle for the accepted
submission format and the real goal.

## Detecting each mechanism

### mass assignment — detect by field inventory

1. `GET` the object; list every field.
2. `POST`/`PATCH` the object's write endpoint; list the fields the form
   sends.
3. The DIFF is the probe list: fields in the model, absent from the form.

`role`, `balance`, `verified`, `permissions`, `plan`, `flags`, `owner`
in the diff are the privileged candidates.

### workflow skip — detect by step enumeration

1. Map the intended order from the JS or the UI (cart→pay→confirm).
2. Call each non-first step directly, skipping earlier ones.
3. A `200` + state change on a skipped call = the precondition lives in
   the flow, not the handler.

Also test the terminal endpoint bare: `/flag`, `/download`, `/admin`
called with zero flow steps.

### state replay — detect by one-time artifacts

Codes, tokens, coupons, one-time links, OTPs, reset links, vote/claim
endpoints. Each is a "should happen once" transition. The detection is
the serial replay: run twice, diff the state.

### numeric boundary — detect by arithmetic fields

Any field multiplied, added, or compared — `qty`, `price`, `discount`,
`tax`, `amount`, `rate`, `fee`, `credits`. The detection is the boundary
alphabet on each field, watched for: `200` on a forbidden value, a total
that goes negative/zero/NaN, or a clamp that reveals the bound.

### scaling-after-check — detect by index transformation

Any index/ID/offset that the code touches before use. In source, look
for: `arr[off + id*S]`, `buf[id << k]`, `ptr + id*stride`, decode-then-
index. Black-box: the different-layer rejection test (see falsifiers).

### unit confusion — detect by implicit units

`price` fields that could be cents-or-dollars, `weight` kg-vs-lb,
`amount` smallest-unit-vs-display-unit. Detect by sending the "other"
unit and reading how it's stored/charged.

### trust-in-earlier-step — detect by echoed values

Hidden form fields carrying prices/totals, state tokens minted upstream,
`step`/`state`/`Referer` values carried across requests. Any value the
server produced earlier and accepts back verbatim is a trust candidate.

## The detection ordering

```
1. bundle_miner        → endpoints + fields (the edge list)
2. GET the object      → the model's field map (mass-assignment targets)
3. happy-path baseline → the imagined workflow, verbatim
4. mechanism sweep     → one probe per alphabet entry, falsifier attached
```

The sweep is cheap — every probe is a single curl. The cost is in NOT
running it: a logic flaw is an edge you only find by walking it.

## Detection anti-signals (when NOT to keep digging this class)

- Every extra field `400`s → strict schema; mass-assignment dead (other
  mechanisms may still live).
- Every skipped step `302`s → real state machine; workflow-skip dead.
- Every replay `409`s → dedup exists; replay dead.
- Every boundary `400`s or clamps → arithmetic validated; boundary dead.

Four dead mechanisms is most of the alphabet — after that, the remaining
logic surface is unit confusion, transforms, and trust-in-earlier-step,
which need the source or the bundle, not more probes.
