# Server-side merge pollution (Node/JS)

A JSON body that is merged — recursively assigned — into a server-side object
can write onto `Object.prototype` through `__proto__`, or onto arbitrary keys
through merge helpers that accept operator-shaped input.

## Probe shapes that worked

**Empty-filter merge** (Secure Notes): send an update containing only your own
note's filter and no content fields, and read the response. Expected: the merge
accepted `__proto__`-shaped or `$rename`-shaped input and the response reflects
a property your own object never had — the write landed on the prototype, not
your note. Falsifier: the update is ignored or rejected for the operator shape;
the merge is not reachable.

```json
{"filter": {"id": "<your-note>"}, "__proto__": {"marker": "pp-probe"}}
```

Then GET any resource and look for `marker` on objects that never carried it —
the signature read is *a property appearing where it was never set*.

**`$rename`/`$` operator shapes**: Mongo-style merges treat `$`-prefixed keys as
operators; a merge helper that does not strip them lets `$rename`, `$set`-like
or `$where`-shaped input act on fields the API never exposed.

## The constructor.prototype deep path

When `__proto__` is sanitized, walk the other route:

```json
{"theme": {"constructor": {"prototype": {"outputFunctionName": "x;__append('[PP-MARKER]');var y"}}}}
```

(Chromatic Aberration — confirmed.) The `constructor` key survives most
`__proto__` filters and reaches `prototype` one level deeper; the polluted key
here was a template's `outputFunctionName`, turning pollution into code
execution when the function was later compiled.

## Falsifier

A probe property set under `__proto__` or `constructor.prototype` never appears
on a later-fetched object — the merge rejects meta keys or the prototype is
frozen. Pollution needs an observable *second* read; a write that lands nowhere
is not the class.

## Traps

- Pollution that lands on a *local* object, not the shared prototype, changes
  nothing other requests can see — verify with a fresh request.
- The gadget must exist downstream: a polluted key is only a finding when some
  code path reads it (template opts, spawn env, config merge, output fns).
