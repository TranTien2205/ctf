# CTF shapes — how prototype pollution shows up in challenges

The verified cards name five real shapes. Each is a known-good carrier
+ sink pair — match the shape, replay the probe.

---

## Shape 1 — Mongoose `$rename` → `__proto__` (SecNotes)

**The observation.** A note-taking app with an update endpoint that
forwards `filter`/`update` to mongoose.

**The chain.** `{"filter":{"id":<own>}, "$rename":{"<existing-field>":
"__proto__.marker"}}` — the rename target path reaches the prototype
on materialization. The gate that opens: a `local`-only check that
reads `config.local` and treats absence as allowed — polluting
`local` flips it.

**The trap.** Send ONLY the filter + `$rename` — content fields in a
broad filter overwrite every doc in the collection. Pin the filter to
your own id.

**Falsifier.** The driver coerces the target to a literal field name —
`__proto__.marker` stored as a string field, never materialized.

## Shape 2 — `constructor.prototype` → EJS `outputFunctionName` (Chromatic)

**The observation.** A render/export endpoint taking a `theme` object
merged into view options; the renderer is EJS.

**The chain.** `{"theme":{"constructor":{"prototype":
{"outputFunctionName":"x;__append('[PP]');var y"}}}}` — `theme` is a
legit nested object, `constructor.prototype` bypasses the `__proto__`
filter, `outputFunctionName` is compiled into the generated function
on the next render.

**The trigger.** The export-preview endpoint renders on demand — a
`2.5s` worker spawn each time, so the prototype write lives inside
that worker's process and dies with it. On a shared instance the same
primitive is RCE-as-renderer.

**Falsifier.** The render uses a pre-compiled template (view cache) —
the polluted option never reaches `new Function`.

## Shape 3 — Bot-relayed write → class pollution (TornadoService)

**The observation.** A write endpoint returning 403 local-only, plus
an admin bot that visits URLs you give it.

**The chain.** The bot's session carries the write for you — the
endpoint is CSRF-able and the bot IS authenticated locally. The
payload is a class-attribute write (Python `__globals__` flip or a JS
`__proto__` write via the bot's own request).

**The sequence.** Fetch a public read for a valid object id → confirm
the write is 403 direct → build a URL/page the bot will POST/merge
from → the bot's session carries the write → the class attribute
flips globally.

**Blast radius.** The polluted setting is global — other players lose
sessions while it's dirty.

## Shape 4 — Hop-by-hop → cache-overflow → DOM-clobber → RCE (NovaCore)

**The observation.** A proxied API where `Connection` header lists a
hop-by-hop header; the app trusts the proxy-injected header.

**The chain.** A token-gated API accepts the request twice — once
plain (401) and once with the proxy-added header listed in
`Connection` — the header smuggles past and changes the cache key or
the resolved identity. The chain continues into a cache overflow → a
DOM-clobbered polyglot → RCE via plugin execution.

**The IDOR/PP join.** The header injection reaches an object merge
that only the proxy's path runs — the merge isn't reachable on the
direct request.

**Falsifier.** The 404 on BOTH arms — the path is wrong, not the
technique.

## Shape 5 — gRPC attribute pollution → eval (Artificial University)

**The observation.** A gRPC service with reflection enabled; the
protobuf message fields map to server attributes.

**The chain.** Field-level `setattr` walks the message schema into a
live Python object graph — a field path reaching an eval-adjacent
global (`__globals__['eval']` or a module attribute the handler
imports) runs it on the next call.

**The carrier.** gRPC metadata + the message's own field names — the
schema reflection names which fields exist.

## The cross-shape rules

- The carrier is always a LEGIT nested object (`theme`, `settings`,
  `config`, `prefs`, `filter`) — the proto key rides inside data the
  API already accepts.
- The sink is always a PROPERTY read with a fallback (`isAdmin`,
  `outputFunctionName`, `local`, `env`) — never a method call you
  control.
- The trigger is always a SECOND request — write now, observe later.
- The marker is always harmless first — `__append('[PP]')` before
  `readFileSync('/flag')`.
- The blast radius is always global — every subsequent requester
  inherits the pollution.
