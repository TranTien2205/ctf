# Prototype / class pollution

**When:** a server-side deep-merge or recursive assignment consumes request
JSON. Signals: `Object.assign`, `_.merge`, `deepmerge`, `qs` parsing into
nested objects, settings/preferences update endpoints.

## Detect (harmless first)

Pollute a harmless property, then READ it back somewhere it surfaces:

```json
{"__proto__": {"argus_probe": "yes"}}
{"__proto__.argus_probe": "yes"}
{"constructor": {"prototype": {"argus_probe": "yes"}}}
```

Read-back channels: a later response that includes the property, a 200 vs
error differential, an admin/debug page, or downstream behavior change
(e.g. a new field appearing). If you cannot observe the property, the
payload proving nothing is a dead end - stop after ~3 variants.

## Exploitable sinks (server-side JS)

Polluted properties that flip behavior when code reads an undefined attr:

- `isAdmin`/`role`/`verified` - privilege escalation if a check reads
  `user.isAdmin` as undefined->polluted
- `shell`/`execPath`/`env` - child_process options
- `outputFunctionName`/`client`/`escapeFunction` - template engines
- `__dirname`/`path` - file operations
- `status`/`headers` - response control

## Client-side variant

URL fragment/query `?__proto__[x]=y` polluting DOM reads -> DOM XSS chains;
only pursue when the front-end parses query into objects (check js_recon
output for `parseQuery`, `$.parseParams`, `qs`).

## Python/Ruby/Java cousins

- Python: class pollution via `__class__`, `__init__`, `__globals__` on
  attribute-merge endpoints; also `__dict__` updates
- Ruby: `marshal`/yaml deserialization overlaps `deserialization`
- Java Jackson: `@class`/`@type` polymorphic typing (see deserialization)

## Falsifier

`__proto__`/`constructor` keys are dropped by the parser or never surface;
no sink reacts after 3 read-back channels tried.

## Severity guide

Privilege or code path change proven: high-critical. Property accepted but
no behavior change found: medium (latent) - say so.
