# Common mistakes — the ways a mass-assignment run goes wrong

## 1. Citing the write echo

`POST` response shows `{"role":"admin"}` — recorded as stored. The echo
is the parser's view; Mongoose `strict` and similar echo bound-then-
dropped fields. The read-back is the store's truth — always GET through
a different endpoint.

## 2. Calling a stored field a finding

`role:"admin"` stored, `/admin` still `403` — the gate reads `is_staff`
or a JWT claim. A stored-but-inert field is a NULL result — the class
bar says so verbatim. Record it; don't cite it.

## 3. Probing spellings, not semantics

`role`, `isAdmin`, `admin_flag`, `ROLE` — four probes, one semantic.
The model answers semantics; a falsifier on `role` likely covers
`isAdmin` too. Probe the SEMANTIC space (privilege, verification,
economics, plan, ownership, workflow) — not the spelling space.

## 4. Skipping the control

`role:"admin"` on read-back — but was `admin` the DEFAULT? The control
pair (`{u,p}` vs `{u,p,role}`) is what attributes the diff. Without it
the admin could be platform default.

## 5. One content-type, one conclusion

`role` dropped on JSON → "class dead". The form path uses a different
parser+binder — `role=admin` form-encoded may bind cleanly. Content-type
falsifier kills ONE cell; the matrix stays open.

## 6. Ignoring the second binder

`POST /register` tight; `PATCH /users/me` wide — probing only the
register endpoint misses the profile binder, which is the usual live
one. Per-endpoint map first.

## 7. Wrong-type probes falsifying prematurely

`role:true` `400`s → conclude `role` dead. The column is string —
`role:"admin"` may bind. One right-type retry per semantic before the
falsifier.

## 8. Mass-spelling sweeps

100 field names × one endpoint — 95 of them absent from the model.
The dictionary is for COVERAGE of semantics, not for volume — run
`binding_probe.py` (its default set is the high-frequency shortlist)
and read the read-back keys first.

## 9. Forgetting the decision leg

`verified:true` stored — never exercised. The verify-skip flag gates
on `verified` — hit the gated endpoint. Storage + exercise = confirm;
storage alone = null.

## 10. Reading the cached view

`GET` returns `role:"user"` — from a cached representation. Add
`?cb=<rand>` or read `/api/me` vs `/api/users/:id` before recording
the falsifier.

## 11. Confusing the class

`{"author_id":1}` forges authorship — file under `web-idor` when the
bug is object ACCESS, `web-mass-assignment` when it's the bound FIELD.
`constructor.prototype` → `web-prototype-pollution`, not here. The
class-boundary module draws the lines.

## 12. PUT wiping the object

`PUT /users/me {"role":"admin"}` — the replace zeroed `username`, the
account broke, the probe looks dead. PUT needs the FULL control body +
extras.
