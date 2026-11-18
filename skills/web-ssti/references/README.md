# SSTI references — navigation

The contract lives in [../SKILL.md](../SKILL.md). This directory
is the operational corpus — pick the file for the stage you're in.

## Detection & fingerprinting

| File | Content |
|---|---|
| `detection.md` | The probe workflow — find render-point, confirm eval, fingerprint |
| `engine-detection.md` | The fingerprint matrix — every engine's delimiters, errors, tells |
| `polyglots.md` | One string, many engines — for unknown/deferred renders |
| `injection-points.md` | WHERE the input can land — param/path/attr/stored/email/pdf |
| `format-string.md` | `str.format`/`f-string`/`%`-format — the adjacent read-only class |
| `error-pages.md` | Forcing + reading stack-traces — the free fingerprint |

## Per-engine depth

| File | Engine |
|---|---|
| `jinja2.md` | Jinja2/Flask — the canonical python stack |
| `twig.md` | Twig/PHP/Symfony |
| `freemarker.md` | FreeMarker/Java |
| `velocity.md` | Velocity/Java |
| `thymeleaf.md` | Thymeleaf/Spring + SpEL + preprocessing |
| `smarty.md` | Smarty/PHP |
| `mako.md` | Mako/Python |
| `django-deep.md` | Django — logic-less ceiling + real leaks |
| `nunjucks-deep.md` | Nunjucks — the Node Jinja2 |
| `ejs-deep.md` | EJS — the Node scriptlet engine |
| `liquid-handlebars-deep.md` | Liquid + Handlebars — the "safe" engines |
| `node-engines.md` | Pug/Handlebars/doT/etc survey |
| `ruby-engines.md` | ERB/Slim/Haml |
| `java-other.md` | Pebble/Jinjava/Groovy/JSP-EL/OGNL |
| `misc-engines.md` | Blade/Volt/Latte/Tornado/etc |

## Escape machinery — by runtime

| File | Runtime |
|---|---|
| `python-sandbox-deep.md` | `__globals__`/`__subclasses__`/bound-helpers — full map |
| `php-gadgets.md` | Twig/Smarty/Blade internals — `|map('system')`, `{php}`, `_self.env` |
| `java-class-model.md` | `.class`/forName/Runtime — Velocity→FreeMarker→SpEL→OGNL |

## Exploitation & bypass

| File | Content |
|---|---|
| `chains.md` | Eval→flag chains by goal — read/exec/forge/exfil |
| `ssti-bypass.md` | Filter/WAF bypass construction — the decision table |
| `advanced-reach.md` | The nightmare combos — no-underscores + no-quotes + no-dots at once |
| `extended-bypass.md` | Per-engine deep evasions — the Jinja2 arsenal detail |
| `blind-ssti.md` | No-output SSTI — OOB/write-to-webroot/time channels |
| `extraction-deep.md` | Enumeration loops, file-read, exfil, error-channel |
| `payload-dictionary.md` | The payload bank — by engine, by goal |
| `cheatsheet.md` | One-page-per-engine compact tables |
| `workflow.md` | End-to-end playbook — phases, falsifiers, evidence |
| `sandbox-taxonomy.md` | The four sandbox failure-modes — which you're in |
| `engine-quirks.md` | Per-engine edge-cases that break payloads |
| `framework-contexts.md` | Where SSTI lives in Flask/Spring/Rails/Express code |
| `email-pdf-artifacts.md` | Deferred renders — mail/PDF/report pipelines |
| `ctf-shapes.md` | Challenge-presentation playbook |
| `tooling.md` | ssti_probe/http_probe/variant_matrix/tplmap/curl |
| `error-pages.md` | Stack-trace mining — engine+version+paths from errors |
| `os-level.md` | Shell-level ops — reverse/bind/recon from exec |
| `field-manual.md` | Minute-by-minute contest playbook |
| `extended-engines.md` | Long-tail engines — Jade/Dust/Beetl/HTTL/Razor/etc |
| `detection-sequences.md` | Ordered probe scripts for each ambiguity case |

## Field notes

`../field-notes.md` — measured findings appended by the loop.
