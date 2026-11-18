# Evidence rules — what proves pollution and what doesn't

The class has a strict proof boundary: the property must appear on an
object you did not write, OR a fallback must change behaviour. Anything
less is a candidate.

---

## 1. The three verdicts and what each needs

| Verdict | Requires |
|---|---|
| `confirms` | the marker on a fresh/foreign object (verbatim response), OR a sink-behaviour change attributable to the polluted property |
| `refutes` | all carriers tried + the control fetch shows no inheritance + a named defense |
| `inconclusive` | the write succeeded but no readback surface exists — the write may have landed where you can't see |

`post-probe` requires `--response` verbatim and checks `--evidence` is
a substring of it — the marker must literally appear in the fetched
bytes.

## 2. What is NOT evidence

- `200 {"ppmarker":"v1"}` on the same object you wrote — local write,
  NOT prototype pollution. The response is just an echo.
- `200` with no marker — ambiguous: could be local, could be dropped,
  could be global-but-unreadable.
- `404`/`302` — the route didn't match; the write never ran.
- `500` — ambiguous: the setter threw (a lead — the proto path was
  attempted) or the body was malformed. The error TEXT is the
  evidence, not the status.
- `201 {"id": <new>}` — a create succeeded; say nothing about the
  prototype.
- "the response is slower" — timing alone is not a confirm without a
  ~20-sample baseline.

## 3. The fresh-object control

The single most-skipped control. For every `confirms`:

```
same session, same second:
  GET /api/<an-object-you-didn't-write>
  → does it carry the marker?
```

If the marker is on YOUR object only, the merge is shallow or the
write is local — `refutes` for the prototype claim (possibly a
mass-assignment finding instead — different class).

## 4. The nonce rule

The marker's value must be unique per probe: `ppmarker-<nonce>`. A
static `ppmarker:1` could come from the framework's own test data or
a cached response — the nonce makes the response's marker
attributable to THIS write.

## 5. The blast-radius disclosure

Record in the ledger what you polluted:

- the key (`__proto__.ppmarker` vs `__proto__.isAdmin` — a semantic
  property has side effects beyond your session),
- the carrier (JSON body to `/api/settings`),
- whether it persisted (the marker still on fresh objects after N
  requests — it usually does until restart).

A semantic property (`isAdmin`, `role`, `allowProtoMethodsByDefault`)
that stays polluted CHANGES THE APP for every later requester — that
is the finding's blast radius and goes in the report.

## 6. The evidence package

For a `confirms` verdict, the package is:

```bash
python3 tools/hooks.py post-probe "$C" --class web-prototype-pollution \
  --hypothesis-id H1 --verdict confirms --evidence-kind class \
  --evidence '"ppmarker-9f3a":"v1"' \
  --response '{"id":7,"name":"x","ppmarker-9f3a":"v1"}'
```

For impact (the sink ran):

```bash
python3 tools/hooks.py post-probe "$C" --class web-prototype-pollution \
  --hypothesis-id H2 --verdict confirms --evidence-kind impact \
  --evidence '[PP-MARKER]<!doctype' \
  --response 'HTTP/1.1 200 OK\n\n[PP-MARKER]<!doctype html>...'
```

`--evidence-kind class` = the write landed; `--evidence-kind impact` =
a security-relevant read of it. Both can be recorded — the second
builds on the first.

## 7. The flag standard

A flag from pollution still goes through `pre-flag`:

```bash
python3 tools/hooks.py pre-flag "$C" --value 'flag{...}' \
  --source "$BASE/api/admin/flag" \
  --evidence '<the response bytes that carried it>'
```

The flag must be IN the response — a flag-shaped string you typed
into a payload that the app then reflects is NOT the flag (it's your
own payload echoed).

## 8. The negative-report format

```
site: POST /api/settings (JSON body merge)
carriers tried: __proto__ flat, nested-1, nested-2,
                constructor.prototype, qs-form, qs-query, dotted-path
readback: GET /api/me + GET /api/fresh — no marker, no diff
denial: lodash 4.17.21 blacklist (constructor segment also skipped)
verdict: refutes
next: merge site on /api/theme? or switch class
```

`refutes` with carriers+denial named is a COMPLETE negative — it
closes the site, not the class; a different merge site may still be
open.
