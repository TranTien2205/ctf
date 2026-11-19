# Case studies — business-logic solves, from the verified card outward

## Case 1 — Pachinko Revisited (picoCTF 2025): the verified card

The only verified chain in this class. The full mechanics live in
`verified-chains.md`; this is the *study* — what the solve teaches about
running logic-flaw probes.

### The observation sequence

1. **Read the client bundle for the accepted format and the real goal.**
   The handout shipped a front-end bundle; the challenge's actual
   submission format and the win condition were in the JS, not the UI.
   Unreferenced constants were dead code — time was saved by ignoring
   them. *Lesson: the bundle is the spec.*

2. **Map accepted ID range from server rejections, not the UI.** The UI
   showed one bound; the server rejected at another. Sending IDs and
   reading rejection SHAPES (not just "rejected") located the real bound.
   *Lesson: three bounds exist — the UI's, the checker's, and the
   effective one after transform. Measure all three.*

3. **No distinguishing signal → change layer.** Malformed-circuit
   variants all produced the same rejection — every probe hit the
   transport checker. Stopping there was the decision that mattered.
   *Lesson: identical rejections across variants ARE a measurement —
   they locate the rejecting layer.*

4. **The transform gap.** `id` was checked raw; the write used
   `off + id*S`. An `id` chosen so `off + id*S` wrapped into instruction
   memory became a 2-byte arbitrary write. *Lesson: ask where the
   transformed address lands — including inside the checker's own code.*

5. **Privileged instructions appended where execution reaches them.**
   The write landed inside the program the CPU itself would run —
   appended instructions executed before halt. *Lesson: a logic flaw's
   sink can be the verifier's own execution path.*

### The transfer

An agent facing a DIFFERENT challenge — say, an index into a shared
data/code region, or a file offset scaled before a write — should not
look for "NAND circuits". It should ask the card's question: **is the
value the checker bounds the same value the sink uses?**

## Case 2 — the registration-field shape (catalogue)

An app binds register fields to the user model. The form sends
`username`, `password`; the model carries `role`, `balance`, `verified`.

```
probe:    POST /register {..., "role": "admin"}
read-back: GET /api/user/probe → "role": "admin"
```

**Why it worked**: the binder merged all body fields into the model —
the convenient default. The allowlist existed only in the imagined
workflow ("users fill in the form"), not in the handler.

**The falsifier that would have fired**: `role: user` on read-back —
allowlist binding — or `400 unknown field` — strict schema.

## Case 3 — the skipped payment step (catalogue)

A checkout flow `cart → pay → confirm`. The `/confirm` handler checked
that a cart exists — not that `paid=true`.

```
probe:    POST /confirm {"orderId": N}   — with no /pay call
read-back: GET /order/N → "status": "confirmed", "charged": 0
```

**Why it worked**: the handler's precondition was "order exists", a
weaker statement than the imagined workflow's "order is paid". The gap
between the two propositions IS the bug.

## Case 4 — the replayed redeem (catalogue)

`POST /redeem {code}` added credit. The code stayed valid — nothing
marked it consumed.

```
baseline:  redeem once → balance +50
probe:     redeem again → balance +50 again
```

**Why it worked**: idempotency wasn't a requirement in the happy path,
so no dedup was built. A `409` on the second POST would have falsified it.

## Cross-case pattern

Every case — verified or catalogue — is the same sentence: **the
implemented state machine permits an edge the imagined workflow doesn't
have.** The probe is always the smallest walk along that edge; the
evidence is always the forbidden state read back verbatim; the falsifier
is always the check that would make the edge impossible.
