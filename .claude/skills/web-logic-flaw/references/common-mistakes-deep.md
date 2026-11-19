# Common mistakes deep — the failure modes that waste sessions

`common-mistakes.md` lists twelve. This module goes deeper on the ones
that actually cost solves — with the recovery for each.

## The re-spelling loop (the Polynomial failure mode)

**The failure**: `role` → `isAdmin` → `is_admin` → `admin` → `userRole`
→ `accessLevel` → `privileges` → `perms` — nine probes, one mechanism,
one proven allowlist.

**Why it's seductive**: each spelling is cheap and the NEXT one might
work. But the falsifier already fired — `role: user` on read-back proves
an allowlist exists, and an allowlist answers every spelling at once.

**The recovery**: after the falsifier, the question is never "which
field name" — it's "which MECHANISM". The alphabet has twelve others.
`decide.py` counts probes per class; the fifth variant is already
spending the budget.

**The subtle version**: `role` on `register` falsified, then `role` on
`PATCH /profile` — that IS a different layer (a different binder), not
a re-spelling. The distinction: endpoint/layer change is legitimate;
field-name spelling on a proven allowlist is not.

## The echo illusion

**The failure**: `POST /register {"role":"admin"}` returns
`{"role":"admin"}` → "confirmed". The response echoed the request —
the framework's `create` returns the bound object, but only allowlisted
fields actually persisted.

**The recovery**: the echo is HALF the test. The read-back (`GET` the
object fresh) is the other half. If they disagree — echo says admin,
read-back says user — the write echoed unbound input. Record the echo
as surface evidence; the read-back decides.

## The stale-state illusion

**The failure**: skip to `/confirm` → `200` → `GET /order/1` shows
`confirmed` → "skip confirmed". But order 1 was confirmed in an earlier
test — the GET read stale state.

**The recovery**: mint a fresh object per probe (fresh cart/order/
account), or read a baseline field you didn't touch (`createdAt`,
`sequence`, `id`) proving the state postdates your probe. The cost of
a fresh object is one POST; the cost of a false confirm is the session.

## The two-variable probe

**The failure**: `quantity=-1&coupon=SAVE50` → negative total. Which
variable? Unknowable — and unrecordable as class evidence.

**The recovery**: one probe changes one variable. If a combination is
the hypothesis (the card's chains DO compose), establish each leg
separately first: `quantity=-1` alone, `coupon=SAVE50` alone, THEN the
combination — three probes, three attributable results.

## The imagined-check trap

**The failure**: "the docs say IDs must be < 100, so 4096 fails" →
never sent. The documented bound and the enforced bound and the
effective bound are three numbers.

**The recovery**: send the value. The Pachinko solve mapped the ACCEPTED
range from rejection behavior — the documented limit was wrong by the
transform's whole scale. Docs describe the imagined check; the response
measures the real one.

## The premature sink hunt

**The failure**: `role: admin` confirmed → immediately `GET /flag` →
`404` → "dead end" → abandon. The admin role reaches an admin *surface*,
not a flag endpoint — `/admin`, `/admin/users`, `/admin/config`,
`/export` — the flag is usually a field inside the admin view, not a
path.

**The recovery**: enumerate the role's reach — the admin paths from the
bundle, the routes in source, the endpoints gated on `role` in access-
control code. The flag is the last step of the chain, not the first
probe after the confirm.

## The serial-vs-parallel confusion

**The failure**: replay blocked serially (`409`) → assume replay dead.
The dedup check itself may have a TOCTOU window — two PARALLEL redeems
both pass the check before either writes.

**The recovery**: serial replay is logic-flaw's probe; the parallel
window is `web-race-condition`'s. Route, don't re-probe — `race_probe`
with `--write-ack`, serial baseline first.

## The mechanism-blind sweep

**The failure**: running ALL boundary values on ALL numeric fields as
one undifferentiated loop — 200 probes, no attribution, budget spent.

**The recovery**: the alphabet is a decision tree, not a list.
`-1` → `400`? validator present → next FIELD. `200` + clamp? clamp —
note the layer. `200` + negative total? confirmed — stop, record,
chain. Each result selects the next probe; the loop without the tree
is what budgets are for stopping.
