# Multi-Parser — the content-type-negotiation and dual-parse shapes

## The "the endpoint picks a parser by Content-Type"

A single endpoint that routes to different parsers by `Content-Type` —
JSON→JSON-parser, XML→XML-parser, form→form-parser. The XXE surface
appears when the XML branch is live but the JSON branch is the default.

```bash
curl -X POST -H 'Content-Type: application/json' -d '{"x":1}'           → 200
curl -X POST -H 'Content-Type: application/xml'  -d '<r>x</r>'          → 200 — the XML branch ran
curl -X POST -H 'Content-Type: text/xml'         -d '<!DOCTYPE...>'     → entity?
```

The verified card `htb-xxe-content-type-branch` is exactly this — the
XML branch on a JSON-looking endpoint.

## The "the same body parses differently by content-type" — the smuggling-adjacent

`Content-Type: application/json` + XML body — the app may `json_decode`
it (fails) OR sniff the `<` and route to the XML parser — the "the
content-type is a hint, not a contract" pattern.

## The "the app reads a field then re-parses it as XML" — double-parse

```json
{"xml": "<!DOCTYPE r [...]><r>&x;</r>"}
```

The JSON parses the outer, then the app extracts `xml` and re-parses —
the XXE surface is inside a JSON field — the outer content-type is a
disguise.

## The "the endpoint accepts both, you pick" — format-negotiation

`?format=xml`/`?format=json`/`Accept: application/xml`/`Accept:
application/json` — the format-parameter picks the serializer — inject
XML via the `format=xml` branch.

## The parser-differential — the proxy sees XML, the backend sees JSON

Two parsers (proxy WAF + backend parser) reading the same body
differently — the proxy checks `Content-Type: application/json` and
passes it, the backend sniffs `<` and parses XML — the WAF never sees
the entity. `web-parser-differential` territory.

## The "the app forwards the body to a second parser" — internal relay

```
POST /api    → the app reads JSON → extracts a field → forwards to
               an internal XML-RPC/SOAP → that parser sees XML
```

The XXE surface is on the INTERNAL service — your input passes through
a JSON layer and lands in an XML parser.

## The "the app parses twice" — the double-parse quirks

`xml->json->xml` round-trips, a `normalize` step, a `schema-validate-
then-parse` — each parse context may have different hardening — the
FIRST parse may be defusedxml-hardened, the SECOND raw `lxml` — XXE
fires on the second pass.

## The "the same file parses by the OS and the app" — upload-dual-parse

An uploaded `.docx` is parsed by the app's own OOXML lib (entities on)
AND by the server's libmagic/Antivirus — two parsers, one file.

## The "the app's parser differs by route" — endpoint-specific

`/api/v1` uses `simplexml` (PHP default — external entities off),
`/api/v2` uses `DOMDocument` with `LIBXML_NOENT` — different codepaths
→ different XXE reality per endpoint — fingerprint each route.

## The "the app's parser differs by input-size" — fast-path vs full

Some stacks use a SAX fast-path for big docs and a DOM for small —
the SAX path may have different entity config than the DOM path.

## Record the parser-per-route

Each route gets its own ledger line — the `Content-Type` that triggered
XML parse + which parser's error fingerprint appeared + which entity
tier reached.
