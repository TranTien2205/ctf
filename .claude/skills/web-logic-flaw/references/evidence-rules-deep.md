# Evidence rules deep — constructing the logic-flaw proof

The shallow rule is "forbidden state, read back verbatim". The deep rule
is about *attribution*: the recorded evidence must make it impossible to
read the result any other way. This module is how to build proof that
survives scrutiny.

## The attribution problem

`balance: 200` means nothing alone. It could be:

- the replay worked (your hypothesis),
- a different request added credit (misattribution),
- the balance was already 200 (stale baseline),
- the field means something else (misread semantics).

Attribution requires controlling every alternative. The evidence bundle:

```
1. baseline-before:    GET /balance    → {"balance": 100}
2. first-apply:        POST /redeem    → {"balance": 150}
3. baseline-mid:       GET /balance    → {"balance": 150}   (stable)
4. replay:             POST /redeem    → {"balance": 200}
5. confirm:            GET /balance    → {"balance": 200}   (independent read)
```

Five rows. Remove any one and an alternative survives:

- Without (1): the 150 might predate your first redeem.
- Without (3): the 150→200 might be another actor.
- Without (5): the 200 might be an echo artifact of the write response.

## Per-mechanism evidence bundles

### mass assignment

```
POST /register {..., "role":"admin"}        → 200 {"role":"admin"}   (echo only)
GET /api/user/probe                          → 200 {"role":"admin"}   (store — class)
GET /admin                                   → 200 {...}             (impact)
```

The GET is the class evidence; the echo alone is surface.

### workflow skip

```
POST /cart → /order/N exists (unpaid)       → baseline
POST /confirm {"orderId":N}   (no /pay)     → 200
GET /order/N                               → "status":"confirmed","charged":0
```

`charged: 0` (or `paid: false`) is the verbatim proof the skipped step
was *required* — the forbidden state is "confirmed AND unpaid".

### state replay

As the attribution section: before/after1/after2 with a stable mid-read.

### numeric boundary

```
POST /cart {"productId":2,"quantity":-1}    → 200
GET /cart                                  → "total": -50
POST /checkout                             → "charged": -50          (impact)
```

The cart showing `-50` is the class; the checkout accepting it is the
impact. A negative cart that 400s at checkout is a confirmed class with
no impact — record it as class-level and keep walking.

### scaling-after-check

```
id=<limit>                                 → accepted (baseline)
id=<limit>+1                               → different-layer rejection (class)
id=<malformed>                             → transport rejection (contrast)
```

The evidence is the *difference between the two rejections* — quote both.
"Different-layer" means: different error text, different status, a 500
where the other gave 400, or silence where the other spoke.

### trust-in-earlier-step

```
step1 response: {"price": 50}  (server minted)
POST /confirm {"price": 1}     → 200
GET /order/N                   → "charged": 1
```

The server-minted `50` vs the charged `1` is the verbatim gap.

## The substring rule

`hooks.py post-probe --verdict confirms` requires `--evidence` to be a
substring of `--response`. Implications:

- Quote the response's exact bytes — `"role":"admin"` including its
  whitespace/quoting as the server emitted it.
- Don't paraphrase: `role was admin` fails the substring check AND the
  evidence standard.
- Save the raw response file; `--response "$(cat resp.txt)"` carries it
  whole.

## What the ledger entry must let a stranger reconstruct

Six months later, someone should be able to read the entry and reproduce
the confirm. That means recording:

- the exact request (method, path, body — not "sent role=admin"),
- the response file's verbatim excerpt,
- the baseline it diffed against,
- the verdict and its grade (class vs impact),
- the falsifier status (what would have killed it — did it fire?).

## Evidence hygiene

- One hypothesis, one evidence bundle — don't merge "I also tried X"
  into another probe's verdict.
- A `confirms` verdict on class evidence is not a `solved` — the flag
  still needs `pre-flag` against its own live response.
- Rebutted alternatives belong in the entry: "fresh object minted at
  T0; balance baseline read twice" is attribution bookkeeping, not
  verbosity.
