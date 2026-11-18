# web-deserialization reference corpus

## Where to start

`../SKILL.md` — the operational contract: magic-byte fingerprint →
corrupted-blob probe → marker/URLDNS → gadget. This directory is the depth
behind each step.

## The decision tree

```
found an opaque blob
 ├─ what are the magic bytes?           → detection.md
 │   ├─ PHP O:/a:         → php-deser.md → php-pop-chains.md → phar-deser.md
 │   ├─ Java aced         → java-deser.md → java-gadgets.md → jndi-injection.md
 │   │                      → java-deep.md (stream internals)
 │   ├─ pickle gAN/80 03  → python-deser.md → python-pickle-deep.md
 │   │                      → python-other-sinks.md (yaml/jsonpickle/npy)
 │   ├─ .NET AAEAAD//wEP  → dotnet-deser.md → dotnet-gadgets.md
 │   │                      → dotnet-viewstate.md
 │   ├─ Ruby BAh          → ruby-deser.md
 │   ├─ YAML !!           → yaml-deser.md
 │   ├─ node _$$ND_FUNC   → nodejs-deser.md
 │   └─ other/unknown     → other-formats.md → fuzzing-sinks.md
 ├─ need the mechanics?   → primitives.md → magic-methods.md
 ├─ filter/waf/signature? → filter-bypass.md → signature-bypass.md
 ├─ stored-then-fired?    → second-order.md
 ├─ what does a CTF look like? → ctf-shapes.md → ctf-recipes.md
 └─ the working loop      → workflow.md → tooling.md
```

## Module index

### Detection & mechanics

- `detection.md` — magic-byte fingerprint table, corrupt-and-diff probe,
  error-signature per parser, falsifiers
- `primitives.md` — what a deserializer actually hands you: controlled
  class-instantiation, the four sub-primitives
- `magic-methods.md` — the per-language hook table: which magic method
  fires when, per language
- `fuzzing-sinks.md` — finding the sink black-box when source is unavailable

### Per-language

- `php-deser.md` — grammar, magic methods, POP anatomy, `S:` type,
  `__wakeup` suppression, `allowed_classes`
- `php-pop-chains.md` — the phpgcc catalog per framework + DIY recipe
- `phar-deser.md` — phar:// metadata deserialization via file-ops
- `php-session.md` — PHP session-handler tricks + `session.upload_progress`
- `java-deser.md` — stream anatomy, `readObject` sinks, ysoserial, JNDI
- `java-gadgets.md` — the ysoserial chain catalog + version picking
- `java-deep.md` — TC_STREAM internals, annotation section, hand-crafting
- `jndi-injection.md` — lookup path, JDK mitigation ladder, marshalsec
- `python-deser.md` — pickle protocols, `__reduce__`, filter bypasses
- `python-pickle-deep.md` — opcode VM, memo, `__setstate__`, builtins paths
- `python-other-sinks.md` — PyYAML, jsonpickle, npy, shelve, msgpack
- `ruby-deser.md` — Marshal internals, ERB-universal, Psych
- `dotnet-deser.md` — the five formatters, TypeNameHandling, ViewState
- `dotnet-gadgets.md` — the ysoserial.net catalog + formatter matrix
- `dotnet-viewstate.md` — ViewState MAC anatomy + machineKey recovery
- `nodejs-deser.md` — node-serialize, funcster, js-yaml, devalue
- `yaml-deser.md` — PyYAML / Snakeyaml / Psych / js-yaml typed tags
- `other-formats.md` — protobuf/bson/msgpack/thrift/XStream/XMLDecoder

### Paths in and out

- `signature-bypass.md` — MAC/signed-blob bypass: keys, `alg=none`, `kid`
- `filter-bypass.md` — byte-blacklist, `allowed_classes`, WAF, mangle
- `second-order.md` — stored-then-deserialized via session/cache/job/db
- `ctf-shapes.md` — how challenges actually deliver the blob
- `ctf-recipes.md` — end-to-end recipes per framework/delivery
- `gadget-index.md` — every public gadget name → what it does, which lib

### Practice

- `workflow.md` — the prove-then-weaponize loop + decision tree
- `tooling.md` — repo tools (real flags) + ysoserial/phpgcc/ysoserial.net
- `evidence-rules.md` — confirm vs inconclusive vs falsifier, the OOB rule
- `error-analysis.md` — read the parser's complaint: each error's meaning
- `common-mistakes.md` — the budget-burning traps
- `payload-dictionary.md` — the categorized payload corpus
- `cheatsheet.md` — the two-column field reference
- `whitebox-hunt.md` — the source-grep patterns per language
- `blind-deser.md` — OOB-only exploitation when nothing reflects
- `polyglot-deser.md` — multi-format smuggling + wrapper tricks
- `gadgets-by-sink.md` — pick the gadget by the sink you want

### The read & fingerprint layer

- `the-initial-read.md` — the first ten minutes: intake order + corrupt-diff
- `format-signals.md` — the request-shape tells before decoding the blob
- `language-fingerprints.md` — per-language grammar micro-tells in the bytes
- `blob-wraps.md` — the encoding layers around the stream: b64/gzip/sig/json
- `deserializer-inventory.md` — every parse-call that can be the sink, per lang
- `per-format-walk.md` — walking a blob whose format is still ambiguous
- `framework-sinks.md` — framework-specific deserialize sinks and wrappers
- `mime-carriers.md` — the MIME/multipart carriers a blob hides inside

### Gadget craft

- `gadget-construction.md` — building a POP/gadget graph by hand, per language
- `gadget-picking.md` — which chain fits the classpath/version measured
- `real-world-chains.md` — the published CMS/framework chains worth memorizing
- `php-object-graphs.md` — PHP nested-object graph shapes and reference tricks
- `advanced-construction.md` — the harder graph shapes: cycles, custom-fmt
- `java-readobject-patterns.md` — the readObject/readResolve/Externalizable
  patterns that fire on deserialize
- `unsafe-reflection.md` — reflection/newInstance sinks reached through deser
- `multi-step-chains.md` — two-object and multi-hop gadget graphs
- `chain-bridges.md` — bridging a deser primitive into a second sink

### Escalation & theory

- `serialize-escalation.md` — prop-injection → file-write → RCE ladder
- `object-primitives.md` — non-RCE payloads: role flips, IDOR objects, config
- `extraction-rce.md` — reading output/flag out of a deser reach
- `sinks-not-flags.md` — the sink is the probe; the flag is a separate read
- `verify-the-flag.md` — the flag-read discipline once the chain fires
- `windows-flags.md` — Windows-target flag paths and payload variants
- `theory-of-deser.md` — why typed-unmarshal is unsafe in one page
- `historic-cves.md` — real-world CVE deser patterns CTF borrows from
- `serialize-hardening.md` — the defense patterns (and what still survives)
- `per-lang-quirks.md` — the small version-dependent quirks per language
- `encoding-channels.md` — unicode/charset/encoding edges the parser allows

### Keys, signatures & ops

- `key-hunt-deep.md` — finding the MAC/encryption key the blob needs
- `signature-bypass.md` — MAC/signed-blob bypass: keys, `alg=none`, `kid`
- `opsec-limits.md` — payload-size, memory, CPU limits on a deser reach
- `testing-lab.md` — standing up a local deser sink to dry-run the payload

### Java depth

- `java-jdbc-jndi.md` — JDBC + JNDI bridge chains
- `java-protocol-servers.md` — RMI/JNDI/IIOP/T3 protocol-server shapes

### PHP depth

- `php-soap-injection.md` — SoapClient SSRF-via-deserialization

## The non-negotiable

A gadget that errors proves nothing — only a parser signature on YOUR
bytes, an OOB callback, or a marker reflected confirms the deserializer ran.
The flag comes from a live response or an OOB-log line, through
`tools/hooks.py pre-flag`. Everything else is a candidate.
