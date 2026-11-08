# Client-side DOM pollution

The merge runs in the victim's browser: a URL parameter, hash fragment, or
stored field is parsed as an object and merged into a client-side config, and
`Object.prototype` picks up keys the page's own code then reads.

## Probe shape that worked (Sattrack)

Load the page with the parameter set to JSON containing a `__proto__` branch
that sets the config key to an array holding a harmless same-origin URL, then
read the rendered DOM and check whether a script element with that source was
appended:

```text
?config={"__proto__":{"scriptSrc":["https://same-origin/m.js"]}}
```

Expected: the polluted key lands on `Object.prototype`, and a code path that
reads `config.scriptSrc` (or loops the object's keys) consumes it — the DOM
gains an element or attribute you never put in the markup. Falsifier: the DOM
is unchanged and `Object.prototype` is clean; the client merge does not exist
or filters the key.

## The gadget chain

Pollution alone is inert; the finding is the *gadget* — a site script that
reads the polluted property:

| Polluted key | Gadget that consumes it |
|---|---|
| `src`, `href`, `srcdoc` | script/iframe element creation |
| `innerHTML`, `html` | DOM-write sinks |
| callback / `on*` names | event-handler assignment |
| `outputFunctionName`, template opts | client-side template compile |

Read the bundle for the sink *first* (`../../web-source-map/SKILL.md`): the
pollutable key is whatever a later line reads from the merged object.

## Falsifier

`Object.prototype` stays clean after the load — the parser is a safe
`JSON.parse` on a plain object, or the merge is not reachable from input. No
prototype write means no DOM pollution.

## Traps

- `?x[__proto__][k]=v` (qs-style) and `?x={"__proto__":...}` reach different
  parsers; send both shapes before concluding.
- A polluted key with no downstream reader is a write that landed nowhere —
  identify the gadget line before claiming the class.
