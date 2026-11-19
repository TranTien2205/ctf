# Case studies deep — the solve mechanics, dissected

## Deep case 1 — Pachinko Revisited: the full forensic read

Card: `knowledge/chains/pico-pachinko-revisited-node-offset-scale-wrap-instruction-overwrite.json`

### What the challenge actually was

An Express service wraps a WASM custom-CPU emulator. Users submit a
NAND circuit description; the emulator loads it into memory and runs it.
The "checker" bounds node IDs; the loader transforms IDs into memory
addresses — and the memory also holds the program's instructions.

### Each step, and the decision it required

**Step 1 — read the bundle, ignore dead code.** The front-end bundle
contained the submission format and constants that looked load-bearing
but were unreferenced. The decision: trust the *executed* code path —
an unreferenced constant is dead code no matter how official it looks.
This saved the session from testing constraints that didn't exist.

**Step 2 — map the real range from rejections.** The UI showed one ID
bound; the server enforced another. The method: submit `id` values and
bucket the rejections by shape (same error text + status = same layer).
The accepted range emerged from behavior, not documentation.

**Step 3 — stop on silence.** Malformed-circuit variants produced
identical rejections — every probe hit the transport layer. The
decision to stop mutating is what found the bug: identical rejections
mean one layer is answering, so the interesting value must get past it.

**Step 4 — the wrap arithmetic.** `id` checked raw; address used as
`off + id*S` in a `2^w`-word space. Choose `id` so the transformed
address wraps into instruction memory → a bounds-checked index becomes
an arbitrary 2-byte write.

**Step 5 — code/data shared memory.** The write lands where the CPU
executes — append privileged instructions after the processing loop so
they run before halt. The logic write becomes code execution because
the interpreter doesn't separate the spaces.

### The generalizable skeleton

```
for any system with:  check(raw) → transform(raw) → sink(transformed)
ask:   is check's range == transform's reachable range?
if not:  the excess range is unvalidated input at the sink.
```

Instances beyond Pachinko:

- array index `id` checked `< N`, used as `arr[base + id*4]` — the
  transform is the stride;
- `offset` checked `< fileSize`, used as `offset + headerSize` — the
  transform is the base;
- `amount` checked `< balance`, debited after an exchange-rate
  multiply — the transform is the rate (unit confusion's parent);
- `page` checked `< maxPage`, used as `page - 1` into a signed index —
  `page = 0` reaches index `-1`.

## Deep case 2 — the allowlist shape (catalogue)

The register endpoint: `User.create(req.body)` where `req.body` merges
the whole JSON body and the model carries `role`. The probe is one
field; the read-back is the proof.

The instructive failure mode: the tester sends `role=admin`, sees it
echoed, and declares victory — without the `GET` read-back. The echo
proves parsing; only a separate read proves binding. Half the "mass
assignment confirmed" reports in unvetted writeups are echo artifacts.

## Deep case 3 — the state-machine gap (catalogue)

`cart → pay → confirm` where `/confirm` checks `order exists`. The gap
is a proposition gap: the handler needs `order.status ∈ {confirmed}` to
run, checks `order != null`, and the imagined workflow required
`order.paid == true`. Three different propositions; the code implements
the weakest.

The verbatim evidence is the pair `confirmed:true` + `paid:false` — one
field says the transition ran, the other proves its precondition didn't.

## Deep case 4 — the dedup-key shape (catalogue)

`/redeem` marks the code consumed keyed on `(userId, code)`. Two probes
open the gaps:

- same `(user, code)`, different `requestId` — if the key is `(user,
  code)` it stays blocked; if it's `requestId` it applies twice;
- cross-user: the code consumed by user A replayed by user B — if the
  key is `(code)` it's blocked; `(user, code)` lets B claim A's code's
  effect.

The dedup KEY is the mechanism — the probes enumerate which fields the
key covers.

## Cross-case: the evidence pattern that never changes

Every case, verified or catalogue, produces the same evidence shape:

1. a baseline pair (manipulation absent → normal state),
2. a manipulated request,
3. a verbatim forbidden state (`role:admin`, `confirmed+unpaid`,
   `balance:+50-again`, `total:-50`, `processed` for an out-of-limit id),
4. a falsifier that could have fired and didn't.

Absent any leg, the claim is a candidate. The cards in
`knowledge/chains/` are what completed bundles look like.
