# Detection workflows — the observation → mechanism → probe paths

Three worked detection paths, end to end — the observation, the
mechanism it names, the probe sequence, and the evidence.

## Path 1 — "the app is a shop"

Observation: `GET /api/user/me` → `{"id":42,"role":"user","balance":100}`;
endpoints `/cart`, `/checkout`, `/redeem`, `/flag`.

Mechanism ordering (cheapest first):

1. `GET /flag` bare — `403` → it checks something.
2. `POST /register` with `role=admin` → read-back `role:user` →
   falsifier (flat) → `PATCH /users/me` same → `role:user` → falsifier
   (update binder too) → mass assignment dead here.
3. `POST /redeem code=WELCOME` ×2 → `+50` then `+50` → CONFIRM replay.
4. balance `100 → 150 → 200` → `POST /buy {"item":"flag-item"}` →
   flag item purchased → `GET /inventory` → flag verbatim.

The walk: replay edge → credit state → purchase edge → flag state.

## Path 2 — "the app is a multi-step form"

Observation: register → verify-email → profile → activate; endpoints
`/step2`, `/step3`, `/activate`; a `session.step` cookie.

Mechanism ordering:

1. `POST /activate` bare on a fresh session → `302` to `/step2` →
   state enforced → where does it live? the cookie is signed or
   unsigned → `session_dissect`.
2. `step` in request body → `POST /activate {"step":3}` → `400` →
   body-carried state not read.
3. cookie `step=3` forged → `POST /activate` → `200`, `active:true` →
   CONFIRM (unsigned cookie) → gated surface → flag.

## Path 3 — "the app is an index checker" (the Pachinko path)

Observation: submit `{nodes:[{id,...}]}` to `/api/check`; docs say
`id < 100`; WASM/custom runtime mentioned in the bundle.

Mechanism ordering:

1. baseline: valid circuit → `200 processed`.
2. `id=101` → `400 "node id out of range"` — the documented bound
   confirmed at transport.
3. `id=abc` → `400 "node id out of range"` — IDENTICAL? → falsifier
   for the transform shape... → OR different text/status/500 → the
   transform ran → CONFIRM the gap.
4. derive `off`, `S`, `w` from source/behavior → compute `id` so
   `off + id*S mod 2^w` lands on the target region → the write probe.
5. append the privileged payload at the collision point → the
   interpreter executes it → flag in output.

The walk: contrast rejection → transform confirmed → arithmetic →
controlled write → execution.

## The meta-pattern

Every path is: observation → cheapest-probe ordering → confirm/falsify
per row → the walk to `s_flag`. The mechanism alphabet is the ordering;
the falsifiers are what make it cheap — each dead row closes a cell in
one probe instead of a spelling session.
