# Boundary and flow — the original reference, expanded

The two shapes this skill was founded on: arithmetic boundaries in
flow arithmetic (`quantity=-1` → negative total) and flow-order
boundaries (skipped steps). This module is the deep read of both —
kept for continuity with the original SKILL.md routing.

## The arithmetic boundary in a flow

A flow `cart → checkout` computes `total = Σ qty·price`. The boundary
question: what does the arithmetic produce for values the flow never
intended?

```
quantity=-1  → item contributes -price → total can go negative
quantity=0   → free item
discount=200 → total -100
price=-1     → negative per-unit
qty=0.1      → fractional — totals rounding
qty=NaN      → total=NaN — comparison-false propagation
qty=1e309    → total=Infinity — overflow propagation
qty=2147483648 → int32 wrap → negative total via overflow
```

Each value tests a different invariant: sign, zero, type, NaN-
semantics, float-overflow, int-width. The verbatim evidence is the
impossible total in a read-back — `total:-50` on the cart, and
`charged:-50` or `refunded:50` at checkout for impact.

## The order boundary in a flow

A flow `cart → pay → confirm → flag` is a line in `Σ*`; the handlers
permit a graph. The order-boundary probes:

| Probe | Edge tested |
|---|---|
| `POST /confirm` bare | terminal with no precondition |
| `POST /confirm` on unpaid order | skipped `pay` |
| `GET /flag` bare | terminal-of-terminals, zero steps |
| `step=3` forged | client-writable state |
| `pay → confirm → pay` | re-entry after terminal |

## The combined shape — the boundary at a skipped step

The flows compose: skip to `confirm` on a `total:-50` cart — the
checkout's own validator may be the SECOND check the boundary has to
pass. Two layers of arithmetic checks, one boundary value probing both.

## Evidence

```
cart read-back:   {"items":[{"qty":-1,"price":50}], "total":-50}
checkout result:  {"status":"confirmed","charged":-50}
order read-back:  {"status":"confirmed","paid":false,"flag":"..."}
```

The three-field verbatim: transition ran (`confirmed`), precondition
absent (`paid:false`), sink reached (`flag`).

## Falsifiers

- `400 quantity must be positive` / silent clamp → arithmetic guarded
- `302`/`400` to earlier step / `paid required` → ordering enforced
- `/confirm` 200 but `status` unchanged → soft no-op — negative, not
  confirm

## The layer questions

- WHERE does `total` compute — client JS (forge), server from cart
  (boundary must enter via items), or server from a carried `total`
  field (trust-in-earlier-step)?
- WHERE does `paid` flip — a webhook (callback trust), the `/pay`
  handler (skip target), or client state (forge)?
- WHERE does the flag read — a field on the confirmed order (chain:
  boundary→checkout→read-back), or a gated endpoint (chain: role/
  skip→surface→flag)?

This module anchors the original `boundary-and-flow.md` routing —
the full mechanism coverage lives in `mechanism-alphabet.md` and the
per-mechanism modules.
