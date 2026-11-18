# Denied Conditions — when the parser says no

## The error strings that mean "hardened"

| Error | Parser | Meaning |
|---|---|---|
| `DTD is prohibited` | .NET | `DtdProcessing.Prohibit` — DOCTYPE dead |
| `DOCTYPE is disallowed` | Java Xerces | `disallow-doctype-decl=true` |
| `EntitiesForbidden` / `DTDForbidden` | Python defusedxml | wrapper refuses entities |
| `Detected an entity reference loop` | libxml2 | expansion blocked or recursive |
| `Entity 'x' not defined` | libxml2/any | the entity wasn't declared (or was stripped) |
| `external entity not allowed` | varies | `nonet`/`allow_external_entities=false` |
| `Failed to load external entity` | libxml2 | the FETCH failed — egress or bad URI — not necessarily hardened |
| `Undefined entity` | SAX | external entity skipped — not expanded |
| `XML External Entity` in a WAF block page | WAF | network-layer block, parser never saw it |
| `MaxCharactersFromEntities` | .NET | amplification cap hit — Billion Laughs |
| `entityExpansionLimit` | Java | same |
| `xmlParseEntityRef` | libxml2 | a raw `&` that isn't an entity — payload malformed |

## Distinguishing "parser refused" from "fetch failed"

- **Parse error BEFORE any network action** — `DOCTYPE is disallowed`,
  `EntitiesForbidden`, `DTD is prohibited` — the ENTITY mechanism is
  dead. XInclude is the remaining door.
- **Parse ok but fetch failed** — `Failed to load external entity`,
  `UnknownHostException`, `ConnectException`, a timeout — the ENTITY
  mechanism is LIVE, the network is dead — the local-DTD hijack or an
  `internal`-URL target still works.

## The XInclude wall — the last door

When DOCTYPE is refused AND `setXIncludeAware(true)` is off / XInclude
not supported — the XML surface is fully closed. Remaining routes:

- a different input point (upload container, a second endpoint, a SOAP
  action)
- content-type-confusion (the body-sniffs-XML case)
- a different bug class on the same surface — file-upload, SSRF direct

## The "entities expand but external fetch blocked" split

Internal `&probe;` echoes → expansion live. External `file://` returns
nothing AND an external DTD never reaches your listener → egress dead
→ in-band file-read via `&x;`-echo or error-channel still viable; if
echo is also suppressed → XInclude or the `data:`-DTD trick.

## The "system id not found" — file doesn't exist vs not resolved

`java.io.FileNotFoundException: file:///etc/paswd` — the URI was
RESOLVED and the file doesn't exist — proof of resolution. Different
from `Entity not defined`/`Failed to load DTD` — which is a dead
mechanism.

## The partial-hardening matrix — which door remains

| Config | internal `&x;` | `file:` ext | `%d` ext DTD | XInclude |
|---|---|---|---|---|
| `disallow-doctype-decl` | — | — | — | maybe |
| `external-general-entities=false` | ✓ | — | — | maybe |
| `external-parameter-entities=false` | ✓ | ✓ | — | maybe |
| `DtdProcessing.Prohibit` | — | — | — | maybe |
| `XmlResolver=null` (no resolver) | ✓ | — | — | maybe |
| `defusedxml` | — | — | — | — |
| `nonet` (libxml2) | ✓ | ✓(local) | — | ✓(local) |

## Recording a dead class

`verdict=refutes`, evidence = the verbatim error, `evidence-kind class`.
The kill-map entry: which config string the parser emitted.
