# Workflow — the business-logic engagement, step by step

## Phase 0 — recon the workflow, not the payload

```bash
# fetch the app; list every endpoint the front-end calls
python3 tools/web/bundle_miner.py --url <bundle-url> --out /tmp/bundle

# the state machine sketch: which endpoints mutate state?
# register / login / cart / checkout / confirm / redeem / flag
```

Deliverable: an ordered list of state-changing endpoints and the fields
each takes. The endpoints ARE the state machine's edges.

## Phase 1 — classify and match

```bash
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --source <dir> --record <challenge>   # if source
python3 tools/skill_select.py web-logic-flaw
```

A chain match is a candidate shape — run its `first_confirming_probe`
against this target before any reuse.

## Phase 2 — baseline the happy path

Run the intended flow once, verbatim:

```bash
curl -i -b "$JAR" -X POST "$BASE/register" -d 'u=probe&p=x'      > r0_register.txt
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&qty=1'    > r0_cart.txt
curl -i -b "$JAR" -X POST "$BASE/checkout" -X POST               > r0_checkout.txt
curl -i -b "$JAR" "$BASE/order/1"                                > r0_order.txt
```

Save every response. Logic evidence is a diff — the baseline is half the
evidence.

## Phase 3 — one probe per mechanism, falsifier attached

Order: cheapest probes first, each with its falsifier ready.

| # | Mechanism | Probe | Falsifier |
|---|---|---|---|
| 1 | mass assignment | `register` + `role=admin` | `role: user` on read-back |
| 2 | workflow skip | `/confirm` without `/pay` | `400/302` to earlier step |
| 3 | numeric boundary | `quantity=-1` | `400` or clamp |
| 4 | state replay | `redeem` twice | `409` second time |
| 5 | boundary alphabet | `0`, `NaN`, `1e309`, `0x10` | `400` per row |

Each probe → `hooks.py post-probe` with the response attached. A
falsifier firing = record `falsified`, next mechanism — not next
spelling.

## Phase 4 — confirm and chain

A confirming signal is a *lead*, not a flag:

- `role: admin` → what does the admin role reach? `/admin`, `/flag`.
- `total: -50` → does checkout accept a negative charge?
- replay doubled the balance → what does the balance buy?

Each confirm opens the next edge in the state machine. The exploit is the
walk to the flag endpoint, one forbidden transition at a time.

## Phase 5 — the flag gate

```bash
python3 tools/hooks.py pre-flag <challenge> --value "<flag>" \
  --source "the response the flag was read from" --evidence "<flag excerpt>"
```

A flag-shaped string not in a live response or supplied artifact is a
candidate. Then `classify_solve.py --chain <id>` files the solve.

## Phase 6 — field notes

Append the probe that worked — and the falsifiers that fired — to
`../field-notes.md` as `proposed`. Confirmed entries come from
`classify_solve.py`.
