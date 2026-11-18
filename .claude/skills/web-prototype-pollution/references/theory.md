# Theory — what prototype/class pollution actually is

The mechanism, the boundary it crosses, and why it is a class of its
own rather than "just a filter bypass".

---

## 1. The mechanism

Every object-oriented runtime resolves property lookups through a
chain:

- JavaScript: `obj.x` → own property → `obj.__proto__.x` →
  `Object.prototype.x` → null.
- Python: `obj.x` → `__dict__['x']` → `type(obj).x` → MRO bases →
  `__getattr__`.

A merge routine that walks attacker-shaped keys and assigns them
recursively can write a property high enough in the chain that every
later lookup inherits it. The write isn't to YOUR object — it's to
the object your object (and every object) inherits from.

The primitive is a WRITE-TO-SHARED-STATE. That is what makes it
different from mass-assignment (a write to your own object) and from
deserialization (a write of whole objects): pollution is a write to
the class/prototype — the shared schema.

## 2. The three conditions

Pollution exists when ALL three hold:

1. **The merge reaches the key** — a recursive/assign routine accepts
   `__proto__`/`constructor`/`__class__`-shaped input.
2. **The write lands on a shared root** — `Object.prototype`, a class
   object, `__globals__` — not a local object.
3. **A sink reads a fallback** — later code does `opts.x || def` on
   an object inheriting the polluted property.

Missing any one and it is not the class: no merge → no write; local
write → own-property (mass-assignment); no sink → the property is
set but nothing reads it (data corruption at most, not a vuln).

## 3. The boundary it crosses

Authorization checks happen at the REQUEST boundary — the input is
checked, the object is fetched, the access decision is made.
Pollution crosses a different boundary: it writes to the PROCESS-
SHARED state that all subsequent requests inherit. It is a
confused-deputy attack where the deputy is the runtime itself — the
merge routine has write-access to the prototype that no request
context restricts.

This is why the check on the REQUEST doesn't help — a filter that
says "no `__proto__` in the body" guards the carrier, but the merge
still runs with whatever it accepts. The check has to be at the
WRITE — the merge's own key handling.

## 4. Prototype vs class pollution

| | JS prototype pollution | Python class pollution |
|---|---|---|
| Shared root | `Object.prototype` (one root) | a class object, `__globals__`, `__builtins__` (many roots) |
| Key | `__proto__` / `constructor.prototype` | `__class__`, `__init__`, `__globals__` |
| The read | `obj.x` falls through proto chain | `obj.x`/`self.x`/`func.globals` |
| The sink | `opts.x || def` pattern | a module attr the code imports |
| Blast radius | every `{}` | every instance of that class / the module's users |

Same mechanism, different graph — JS has one root (everything is an
object), Python has many (each class its own MRO).

## 5. The "why it works" — the setter

`dest.__proto__ = x` doesn't write an own property — it calls the
`__proto__` accessor's SETTER, which replaces `dest`'s prototype with
`x`. Two different write paths:

- `dest.__proto__ = x` → setter → `dest` inherits `x`
- `dest["__proto__"] = x` → bracket-write → ALSO the setter on plain
  objects
- `Object.defineProperty(dest, "__proto__", {value: x})` → defines an
  OWN property named `__proto__` — no setter — does NOT pollute

The first two pollute; the third is the safe idiom. A merge using
`defineProperty` or `Object.create` is safe; a merge using `=` or
`[]` writes through the setter.

## 6. The payoff model

A polluted property is worthless until a sink reads it. The sink
reads it when the app's own objects lack it — the check becomes
`opts.x || default` where `opts` is a fresh object with no `x` —
your polluted `x` is the fallback that fires. The pattern that pays:

```
the app:   function f(opts) { return opts.x || safeDefault; }
you pollute:  __proto__.x = yourValue
the call:    f({}) → yourValue    ← the fallback read it
```

The gadget is the PAIR of a property-name the app reads
conditionally and a sink that trusts the value it gets.

## 7. Why it composes with other classes

Pollution is a WRITE primitive — what it buys is the next class's
sink:

- PP → template options → SSTI/RCE (the template's own compile)
- PP → spawn env → command injection
- PP → `isAdmin` → authz bypass
- PP → url/hostname → SSRF
- PP → deserialization helpers → the deser class
- PP → `__class__` → attribute-write → arbitrary Python object graph

The class is a chain component — a write primitive that escalates a
filter/merge flaw into whatever the app reads next. That's why the
SKILL routes you to `gadget-index.md` before payloads: the property
you write IS the next bug's trigger.
