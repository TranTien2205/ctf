# Evidence rules deep — the confirm/falsify standard, formally

## The two-observation requirement

A mass-assignment confirm needs BOTH, verbatim:

1. **storage** — the extra field appears in a read-back through a
   DIFFERENT endpoint than the write;
2. **decision** — the bound field changes a gated decision (route,
   total, state).

One alone: stored-but-inert = NULL result (the class bar); decision-
without-store = attribution confusion. The pair is the confirm.

## The verbatim requirement

`post-probe --verdict confirms` requires `--evidence` to be a substring
of `--response` — the gate asserts the quote is real, not paraphrased.
Quote the read-back's exact bytes: `"role":"admin"` as it appears in
the JSON.

```bash
# class evidence
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me {\"role\":\"admin\"}" \
  --verdict confirms --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"admin"' --response "$(cat rb.json)"

# impact evidence
python3 tools/hooks.py post-probe <ch> \
  --request "GET /admin (new state)" \
  --verdict confirms --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind impact \
  --evidence '200 + "users":' --response "$(cat admin.txt)"
```

`--evidence-kind class` for the stored-field diff; `impact` for the
decision diff — different kinds, different response files.

## The control requirement

Every confirm needs a CONTROL pair — the documented body vs the canary
(+ONE field). `role:"admin"` on the canary's read-back means nothing
until the control's `role:"user"` is on record. Byte-identical
canary/control = the falsifier; differing = the bound field.

## The attribution rule

ONE extra field per canary. `{"role":"admin","verified":true}` — the
diff can't be attributed to either; split into two canaries. The
control/canary pair is the experimental design; violating it breaks
attribution.

## The read-back rule

The write's own response (the echo) is NEVER storage evidence — it
shows the parser's view, not the store's. Mongoose `strict` echoes
bound-then-dropped fields; serializers show bound-then-hidden fields.
The `GET` through a DIFFERENT endpoint is the store's truth.

## What never confirms

- **the echo**: `{"role":"admin"}` in the POST response — parse
  reached, storage unproven;
- **a `200` alone**: registration succeeds for ordinary users;
- **a stored field changing nothing**: `role:"admin"` stored, `/admin`
  `403` — inert, null result;
- **a field name in an error**: `"role must be one of: user,admin"`
  — the field exists, a candidate not a write;
- **a cached read-back**: stale `role:"user"` — re-GET fresh;
- **two fields in one canary**: unattributable diff;
- **a chain card**: `web-logic-flaw`'s card isn't this class's proof;
- **catalogue confidence**: nothing here has solved mass-assignment —
  say so.

## The falsifier record

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me {\"role\":\"admin\"}" \
  --verdict falsified --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind class \
  --evidence 'rb "role":"user" = control' --response "$(cat rb.json)"
```

With the DEPTH annotated in field-notes: endpoint/content-type/binder-
family/model — which cell died.

## The serializer-hidden caveat

A field stored but never serialized is provable only by the DECISION —
the read-back can't see it. Record "stored, serializer-hidden" and
exercise the gate; don't falsify on read-back absence alone.
