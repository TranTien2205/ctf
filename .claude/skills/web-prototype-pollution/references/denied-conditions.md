# Denied conditions — the defenses that actually close the class

Record the defense that fired; each is a falsifiable negative that
names which path is dead and which stays open.

---

## 1. Frozen/null-prototype defenses

| Defense | What it does | What it leaves open |
|---|---|---|
| `Object.freeze(Object.prototype)` | every proto write no-ops/throws | nothing — the whole class is closed server-side |
| `Object.create(null)` merge targets | the target has no proto to walk | a DIFFERENT merge on a real object |
| `Map`/`Set`/`WeakMap` stores | no prototype keys exist | — |
| `Object.preventExtensions(target)` | new props rejected on the target | pollution on the SOURCE's proto |
| `Object.seal(target)` | same | same |
| `Symbol`-keyed config | props keyed by symbol | — |

`Object.freeze(Object.prototype)` is the hard wall — test it first
with a known-good pollution (`{"__proto__":{"m":1}}` + a fresh object
fetch); if the marker never lands, the wall is real and the class is
closed for this app.

## 2. Merge-layer guards

| Guard | What it does | Bypass |
|---|---|---|
| `key !== '__proto__'` check | literal-name blacklist | `constructor.prototype` |
| `__proto__|constructor|prototype` blacklist | lodash ≥4.17.21 fix | a DIFFERENT merge library the app also uses |
| `hasOwnProperty` on target | skips constructor (it exists) | new keys only — pollute a NEW prop the sink reads |
| `Object.keys`/`for..of` iteration | `__proto__` isn't an enumerable own key on src | — wait, it IS an own property after JSON.parse... |
| schema validation (ajv/zod/joi) | drops unknown keys | a schema-permitted WRAPPER key containing `__proto__` |
| `JSON.parse` + `Object.assign` | shallow copy — `__proto__` lands as data | a DEEPER merge downstream of the assign |
| `structuredClone`/`{...}` spread | own enumerable only | a later recursive merge |

The `Object.keys` row's nuance: `JSON.parse` creates `__proto__` as
an own-enumerable property — so `Object.keys(src)` DOES include it
and `dest[k]` triggers the setter. The guard that actually works is
`Object.keys(src).filter(k => !BLOCKLIST.has(k))` — the blacklist,
not the iteration.

## 3. Typed-property defenses

- a `class User { set isAdmin(v){throw} }` — typed setter throws on
  the authz property — 500 on the write; the error is your signal.
- `getter`-only properties — write fails silently.
- `Proxy` wrappers intercepting `set` — `set` trap rejects `__proto__`
  keys; the proxy's other traps may still leak.

## 4. The "read is not a write" denial

The sink reads `opts.x || default` — you polluted `x`, but the sink
object is built by `Object.create(null)` or a `Map` — the read never
walks the prototype. Pollution landed but no sink consumes it. Record
the sink's construction as the denial, not the write.

## 5. Layer-specific denials

| Layer | Denial |
|---|---|
| Parser | `qs` in `simple` mode keeps `__proto__[x]` literal — no nested key |
| Schema | zod/joi drops unknown keys before the merge |
| ORM | mongoose `strict` drops unknown schema paths |
| Serializer | `toJSON`/`toObject` strips the proto-field on read |
| View cache | template compiled once at boot — no recompile to hit |
| Immutable proto | `Object.freeze(Object.prototype)` — global wall |
| Null-proto root | `Object.create(null)` options objects |

Each is a DIFFERENT wall; name which one your readback showed.

## 6. The "won't be triggered" denial

Pollution landed; the sink never runs:

- `spawn` only fires on a scheduled job — the trigger isn't
  requestable.
- `compile` only runs on admin render — the trigger is role-gated
  (and PP bypasses authz only when a sink is reachable as YOU).
- a `fork`/worker path only hit on a specific event.

The class is proven; the impact is gated. Record the pollution as
confirmed and the trigger as blocked-by-role — escalate via a role
gadget or a bot-relay, not by re-writing the property.

## 7. Recording the denial

```
site: POST /api/settings {"__proto__":...}
carrier: JSON body → merged into config
write: ppmarker absent on fresh-object readback
denial: frozen Object.prototype — the fresh object carries nothing
verdict: refutes (class closed on this stack)
next: none — switch class entirely
```

A denial named to its layer saves the next attempt from re-running
the same carriers — `decide.py` counts it toward the budget and
moves the strategy on.
