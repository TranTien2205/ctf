# Whitebox hunt — finding the logic flaw in source before any probe

When the handout ships source, the state machine is readable directly.
The hunt is a grep-driven walk: find the transitions, read their
preconditions, compare to the imagined workflow.

## Step 1 — enumerate the transitions

```bash
# Express/Node
grep -rn "router\.\(get\|post\|put\|patch\|delete\)" --include="*.js" src/
# Flask
grep -rn "@app.route\|@bp.route" --include="*.py" .
# Rails
cat config/routes.rb
```

Every route is a `δ` edge. Sort into create / transition / terminal.

## Step 2 — read each transition's precondition

For every handler: what does it check before mutating? The grep table:

```bash
# the checks — what pre() actually asserts
grep -rn "if.*paid\|if.*verified\|if.*step\|if.*status\|if.*role" src/
# what's conspicuously absent around mutations
grep -rn "update\|create\|save\|findByIdAndUpdate" src/
```

The gap is the difference between `pre(t)` as coded and the workflow's
required preconditions. `/confirm` checking `order != null` where the
flow needs `order.paid == true` — one line, found by reading.

## Step 3 — the binder audit

```bash
# merge-all patterns — the mass-assignment fingerprints
grep -rn "req.body" src/                          # Express
grep -rn "params\[\|params.permit\|params.require" app/  # Rails
grep -rn "request.form\|request.json\|request.data" .      # Flask/Django
grep -rn "fillable\|guarded" app/Models/                    # Laravel
```

- `Model.create(req.body)` / `{...req.body}` / `Object.assign(user,
  req.body)` → merge-all, every model field bindable.
- `pick(req.body, [...])` / `params.require(:user).permit(...)` /
  `forms.ModelForm` with `fields` → allowlist, the falsifier exists in
  code — check which ENDPOINTS share the model; `PATCH` often has its
  own binder.

## Step 4 — the arithmetic audit

```bash
grep -rn "qty\|quantity\|price\|total\|amount\|discount\|balance" src/
```

For each arithmetic site: are the operands checked for sign/zero/NaN/
range BEFORE the multiply-add? `total += qty*price` with `qty` only
checked `!= 0` is the negative-total site, file:line.

## Step 5 — the transform audit (the Pachinko pattern)

```bash
grep -rn "offset\|scale\|stride\|\* sizeof\|<< \|index \* \|addr" src/
```

For each `index → transformed` site: does the check bound the raw index
while the sink uses the transformed value? `id < LIMIT` then
`mem[off + id*S]` is the card's shape, file:line.

## Step 6 — the state audit

```bash
grep -rn "session\.\|cookie\|state\|step" src/
```

Where does the flow's state live? `req.session.step` (server) vs
`req.cookies.step` (forgeable if unsigned) vs `req.body.step` (client-
supplied directly). The third is a skip by construction.

## Step 7 — the uniqueness audit

```bash
grep -rn "redeem\|claim\|refund\|used\|consumed\|redeemed" src/
```

A one-time action needs a checked-and-set marker. Find the mark —
`code.used = true` — then ask: is it atomic, is it checked before the
effect, is it scoped right? `db.codes.findOne({code})` + later
`code.used = true` is non-atomic AND check-separated — serial replays
between find and set are the TOCTOU window (route to race if the serial
replay still falsifies).

## Step 8 — map findings to probes

Every source find becomes a black-box probe:

| Source find | Probe |
|---|---|
| `Model.create(req.body)` | `register` + `role=admin` → read-back |
| `confirm` missing `paid` check | POST `/confirm` bare → read-back |
| `code.used` set after effect | redeem twice serially |
| `id < LIMIT` + `mem[off+id*S]` | `id` past limit → diff rejection layer |
| `qty != 0` validator | `qty=-1` → cart read-back |

The source names the hypothesis and its file:line; the probe produces
the evidence. `classify.py --source` and `chain_match.py --source`
automate the first pass — this hunt is what runs when they don't fire
or when the matched card's probe falsified.
