# Workflow skip deep — the state-machine internals behind the skip

`workflow-skip.md` covers the probe. This module is the mechanism's
internals: where flow state lives, how handlers enforce (or don't)
order, and the full skip algebra.

## Where flow state lives — the four homes

| Home | Code shape | Forgeability |
|---|---|---|
| server session | `req.session.step`, `session['step']` | real enforcement — falsifier |
| signed cookie | itsdangerous/JWT `step` | readable, not writable w/o key |
| unsigned cookie | `req.cookies.step` | direct forge |
| request param | `req.body.step`, `?step=` | attacker-supplied — always live |
| nowhere | terminal endpoint standalone | bare GET — the zero-cost probe |

The skip probe's follow-up depends on the home: server session → try
the terminal bare or a sibling object; cookie/param → forge it; nowhere
→ done.

## The handler idioms

```js
// weakest — existence only
if (!order) return 404;

// weak — flag set by a client-readable carrier
if (req.body.step < 3) return redirect('/step2');
if (req.cookies.step !== '2') return redirect('/step1');

// real — server-tracked transition
if (session.step < expectedNext) return 302;

// the terminal that checks nothing
app.get('/flag', (req,res) => res.send(FLAG));
```

Read the source for which idiom ships; black-box, the skip probes
distinguish them by result.

## The skip algebra

For flow `S1 → S2 → S3 → S4`:

| Skip | Probe | Tests |
|---|---|---|
| terminal only | `S4` bare | does S4 check ANY state? |
| interior | `S1 → S4` | does S4 need S2/S3? |
| reorder | `S3 → S1 → S4` | is the order itself a check? |
| backward | `S4 → S1` | does terminal state rewind? |
| duplicate | `S1 → S1 → S4` | does a repeated step corrupt state? |
| branch | `S1 → S2b(optional) → S4` | does optional satisfy required? |
| method | `GET /s4` | is the transition method-bound? |
| carrier | `step=4` in cookie/param/body | is state client-writable? |

Each row is one probe with its own baseline — the algebra enumerates
the edges `L' \ L` adds to the imagined line.

## The impossible pair — the verbatim evidence

```
{"orderId": 1, "status": "confirmed", "paid": false, "charged": 0}
```

`status` says the terminal ran; `paid`/`charged` say its precondition
didn't. Both fields must appear in the same read-back — one proves the
transition, the other proves the skip.

## The soft-skip trap

Some handlers `200` on precondition-fail but do nothing:

```js
app.post('/confirm', async (req,res) => {
  if (!order.paid) return res.json({ok: true});   // silent no-op
  order.status = 'confirmed';
});
```

A `200` is not the forbidden state — the read-back (`order.status`)
decides. Soft skips produce `200` + unchanged state: a negative, not a
confirm.

## The parallel-session skip

State server-side but sessions cheap: two sessions sharing an object —
session A does step 1, session B calls step 3 on the same `orderId`.
If state is per-OBJECT not per-SESSION, B's call may see A's step —
or the object's state may lag both. A different probe for the shared-
state home.

## The skip's flag reach

Skipped terminal states usually carry the flag as their payload —
the confirmed order's `flag` field, the activated account's gated view,
the completed flow's reward. The confirm's read-back IS often the flag
response.
