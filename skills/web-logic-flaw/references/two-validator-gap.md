# Two-validator gap — two checks disagree on the same boundary

Two validators guard the same boundary and disagree — the client-side check
rejects, the server-side accepts; or the transport validator rejects, the
application checker accepts. The gap between them is the attack surface.

## The mechanism

```
validator A (transport/proxy/client): accepts ids 1..65535
validator B (application checker):    accepts ids < 0x1000

the gap: ids in [0x1000, 65535] pass A, reach B's different rule
```

Or the inverse — the boundary that passes the outer check but the inner
check treats differently. The Pachinko shape: the bounds check runs on the
pre-scaling value; the scaling transform produces an address in a region
the check was meant to exclude.

## The detection

### Map the validators

Every value passes through layers — each layer may check:

```
client JS → transport/proxy → app framework → route handler → checker/lib
```

For each layer, name the limit it enforces:

| Layer | The check it runs | The evidence |
|---|---|---|
| client JS | `input.max`, `type="number"`, `if (x > n)` | the JS bundle |
| transport | nginx `client_max_body_size`, WAF rules | response headers, error page signature |
| framework | `param :id, Integer, max: n` | the route definition (white-box) |
| route handler | `if (id > limit) return 400` | the handler source |
| checker/lib | `assert address < SIZE` | the library source |

The gap is where two layers name different limits — or where one layer
checks the pre-transform value and a later transform changes it.

### The disagreement signals

- The UI says "ids 1-99" but the API accepts 100+ — the UI limit is not
  the server limit.
- The error messages differ by range — one range gets "invalid", another
  gets "not found" — two different checks are firing.
- The response differs between `curl` and the browser — a client-side check
  the `curl` bypasses.
- The docs say one limit, the observed rejections name another.

## The probe

```bash
# the boundary value — inside one validator's limit, outside the other's
curl -i -b "$JAR" -X POST "$BASE/api/check" -d 'id=4096'   # =0x1000

# compare: a value both validators accept
curl -i -b "$JAR" -X POST "$BASE/api/check" -d 'id=1'

# compare: a value both validators reject
curl -i -b "$JAR" -X POST "$BASE/api/check" -d 'id=70000'
```

## The confirmation

The two validators disagree — the gap value produces a different response
from both the in-range value and the out-of-range value:

```
id=1     → 200 {"status": "ok"}          (both accept)
id=4096  → 200 {"status": "processed"}   (transport accepts, checker treats
                                          differently — the gap)
id=70000 → 400 {"error": "out of range"} (transport rejects)
```

The gap value reaching the inner checker — and being processed by a
different rule — is the confirmation.

## The falsifier

The two validators agree — the boundary is the same:

```
id=4096  → 400 {"error": "invalid id"}   (same rejection as id=70000)
```

Both ranges rejected identically — a single validator governs, no gap.

## The disagreement shapes

| Shape | The gap | The payoff |
|---|---|---|
| client vs server | the JS limit is looser/tighter than the server | bypass the client check — `curl` the server |
| proxy vs app | nginx/WAF passes what the app treats differently | the app sees a value the proxy normalized |
| transport vs checker | the protocol limit differs from the logic limit | reach a code path the logic assumed unreachable |
| pre-check vs post-transform | the check runs before the scaling | the transformed value escapes the checked range |
| two route validators | `param` validation differs from the handler's own check | craft a value that passes one, fails the other |
| doc vs observed | the documented limit differs from the real one | the real limit is wider — or narrower |

## The Pachinko shape

```
step 1 — read the client bundle: GOALS.xor is referenced, only GOALS.flip
         exists — dead code, do not believe the reference
step 2 — map the id range from rejections: transport accepts 1..65535,
         checker accepts < 0x1000 — the gap
step 3 — stop probing when a mechanism produces no signal: unassigned
         nodes read 0, ~50% pass an oracle by chance — false leads
step 4 — pick an index whose post-scaling address wraps into instruction
         memory: 0xfff inverted 0xf000, scaled 0xe000, +0x2000 & 0xffff = 0
step 5 — the 2-byte write supplies the call the program never makes —
         the flag routine's instructions land after the loop
```

## The evidence rules

- The disagreement must be verbatim — two responses, different status or
  body, on adjacent values.
- Name the two validators — "the transport accepted X, the checker
  rejected/accepted it differently" — not "the boundary is weird".
- A crash at the gap is not a confirmation — a `500` proves the value
  reached a new code path, not that it was processed differently.

## The traps

- **The UI's limit is a hint, not the boundary.** The real limit is the
  observed rejection — probe it, do not read it off the form.
- **Error-message differences are the map.** "invalid" vs "not found" vs
  "forbidden" name different checks firing.
- **The checker may normalize before checking.** `id` parsed as int, then
  bounded — `0x1000` vs `4096` vs `"0x1000"` may hit different parsers.
- **A `400` on the gap value proves nothing alone.** Which validator
  rejected it? The error body names the layer.
