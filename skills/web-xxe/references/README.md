# XXE reference map

This directory belongs to the canonical `web-xxe` class skill.
Open the named file after the first probe; do not read the whole directory.

## Choose by observed signal

### Detection and confirmation
| Signal or task | Open |
|---|---|
| Any XXE question — start here | `detection.md` |
| The entity needs a concrete document shape | `content-type-confusion.md` |
| Layer-by-layer yes/no detection | `detection-oracle.md` |
| The full signal-and-falsifier map | `detection-full.md` |
| Ready probe corpus per tier | `detection-payloads.md` |
| The observable catalog | `detection-signals.md` |
| The mechanism/theory | `theory.md` |

### In-band read (echo visible)
| Signal or task | Open |
|---|---|
| `&x;` expands, the file content echoes | `file-read.md` |
| The read ladder, deep paths | `file-read-deep.md` |
| Source-code read — drives the next read | `source-code-read.md` |
| `/proc`/env/secret paths | `env-secret-read.md` |
| File with `<`/`&`/`]]>` breaks the parse | `cdata-wrapping.md` |
| Read a slice / member of a file | `fragment-read.md` |

### Blind / OOB (echo suppressed)
| Signal or task | Open |
|---|---|
| Standard blind — param-entity + DTD | `blind-xxe.md` |
| The exfil-DTD forms | `external-dtd.md` |
| Deep blind techniques | `blind-techniques.md` |
| Deep exfil compositions | `blind-exfil-deep.md` |
| Error-channel exfil | `error-based.md`/`errors-deep.md` |
| Zero-egress — reuse on-disk DTDs | `local-dtd-hijack.md` |
| URL/encoding safety of the content | `exfil-encoding.md` |
| The listener side | `oob-listener-deep.md` |
| OOB channels ranked | `oob-channels.md` |
| DTD templates to serve | `exfil-dtd-templates.md` |

### The no-DOCTYPE doors
| Signal or task | Open |
|---|---|
| `DOCTYPE` refused — XInclude | `xinclude.md`/`xinclude-deep.md` |
| Non-entity fetchers (schemaLocation, xml-stylesheet, NOTATION) | `parser-abuse.md` |
| DTD-grammar features | `xml-structure-abuse.md`/`dtd-features.md` |

### The fetch-is-the-impact
| Signal or task | Open |
|---|---|
| Entity = internal URL (SSRF) | `ssrf-via-xxe.md` |
| The URI-scheme matrix | `protocol-handlers.md`/`uri-schemes-deep.md` |

### Upload / container surfaces
| Signal or task | Open |
|---|---|
| `.svg` upload | `svg-xxe.md` |
| `.docx`/`.xlsx`/`.odt` | `ooxml.md`/`ooxml-deep.md` |
| `.plist`/`.rss`/`.gpx`/etc | `misc-formats.md` |
| Content-Type confusion (JSON→XML) | `content-type-confusion.md` |

### Protocol surfaces
| Signal or task | Open |
|---|---|
| SOAP/XML-RPC | `soap-wsdl.md`/`soap-deep.md` |
| SAML | `saml.md` |
| XSLT/`xml-stylesheet` | `xxe-to-rce.md`/`parser-abuse.md` |

### Per-parser / per-stack
| Signal or task | Open |
|---|---|
| Parser defaults + errors | `parser-specifics.md` |
| Deep per-parser matrix | `parser-matrix-deep.md` |
| Per-library notes | `xml-libraries.md` |
| Java-specific | `java-specific.md` |
| PHP-specific (`php://`, `LIBXML_*`) | `php-specific.md` |
| Hardening configs and gaps | `hardening-configs.md` |
| Parser state machine | `parser-state-abuse.md` |
| Content-type/dual-parse shapes | `multi-parser.md` |
| The parse pipeline | `parser-pipeline.md` |

### DoS / expansion
| Signal or task | Open |
|---|---|
| Billion Laughs / amplification | `billion-laughs.md` |

### Evasion and filters
| Signal or task | Open |
|---|---|
| WAF/filter bypass | `filter-bypass.md` |
| Encoding disguises | `utf-encodings.md` |
| XPath / XQuery boundary | `xpath-adjacent.md` |

### Workflows and evidence
| Signal or task | Open |
|---|---|
| The ordered ladder | `workflow.md`/`exploit-ladders.md` |
| Read-to-impact chains | `exploitation-paths.md` |
| Ready request bodies | `exploit-templates.md`/`payload-dictionary.md` |
| HTTP send recipes | `curl-recipes.md` |
| The repo tools | `tooling.md` |
| Evidence rules | `evidence-rules.md` |
| Denied conditions (errors) | `denied-conditions.md` |
| Traps that burn budget | `common-mistakes.md` |
| CTF shapes | `ctf-shapes.md` |
| Whitebox source hunt | `whitebox-hunt.md` |
| Second-order | `second-order.md` |
| Attack-defense | `attack-defense.md` |
| DTD injection | `dtd-injection.md` |
| Historical CVEs | `historical-cves.md` |
| Real-world cases | `real-world-cases.md` |
| Field manual tables | `field-manual.md`/`cheatsheet.md` |
| The long tail | `extended-corpus.md` |
| XXE → RCE | `xxe-to-rce.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open the named file when the observed signal calls for it — the files are
action-oriented; each starts with the first probe, the expected signal,
and the falsifier. `../field-notes.md` carries the verified observations.
