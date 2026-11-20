# Corpus index - web-ssrf

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

Families present in this corpus, counted from disk. Open the
family's own index or the module whose name matches the
question - do not restate their content here.

| Prefix | Modules | Files |
|---|---|---|
| `README-*` | 1 | `README.md` |
| `advanced-*` | 1 | `advanced-reach.md` |
| `blind-*` | 1 | `blind-ssrf.md` |
| `bypass-*` | 1 | `bypass.md` |
| `cheatsheet-*` | 1 | `cheatsheet.md` |
| `cloud-*` | 1 | `cloud-metadata.md` |
| `common-*` | 1 | `common-mistakes.md` |
| `crlf-*` | 1 | `crlf-injection.md` |
| `ctf-*` | 1 | `ctf-shapes.md` |
| `detection-*` | 1 | `detection.md` |
| `dns-*` | 1 | `dns-rebind.md` |
| `egress-*` | 1 | `egress-blocked.md` |
| `error-*` | 1 | `error-analysis.md` |
| `evidence-*` | 1 | `evidence-rules.md` |
| `fastcgi-*` | 1 | `fastcgi-gopher.md` |
| `fetcher-*` | 2 | `fetcher-fingerprint.md`, `fetcher-matrix.md` |
| `file-*` | 1 | `file-read.md` |
| `flag-*` | 1 | `flag-locations.md` |
| `framework-*` | 2 | `framework-checks.md`, `framework-sinks.md` |
| `gopher-*` | 1 | `gopher-deep.md` |
| `host-*` | 1 | `host-header-ssrf.md` |
| `internal-*` | 3 | `internal-pivot.md`, `internal-routes.md`, `internal-services.md` |
| `json-*` | 1 | `json-params.md` |
| `neg-*` | 1 | `neg-shapes.md` |
| `payload-*` | 1 | `payload-dictionary.md` |
| `probe-*` | 1 | `probe-sequences.md` |
| `protocol-*` | 1 | `protocol-smuggling.md` |
| `redirect-*` | 1 | `redirect-chains.md` |
| `request-*` | 1 | `request-shapes.md` |
| `second-*` | 1 | `second-order.md` |
| `taxonomy-*` | 1 | `taxonomy.md` |
| `theory-*` | 1 | `theory-primitives.md` |
| `tooling-*` | 1 | `tooling.md` |
| `unix-*` | 1 | `unix-socket.md` |
| `url-*` | 1 | `url-parsing.md` |
| `webhook-*` | 1 | `webhook-deferred.md` |
| `whitelist-*` | 1 | `whitelist-shapes.md` |
| `work-*` | 2 | `work-boundary2.md`, `work-closing-checklist.md` |
| `workflow-*` | 1 | `workflow.md` |

## Reading order

1. `../SKILL.md` - first probe, falsifier, confirm shape, traps.
2. The `q-*`/`work-*` module matching the question asked.
3. The family module the question lands on.
4. A `*-route` card for the next family when the current one is spent.

## Discipline

Every module here is one piece of the corpus. A claim is a verbatim
response excerpt or artifact record passed through `tools/hooks.py` -
never a line from this index, which is routing information only.

## Budget note

Scheme probes are one request each against the same fetch point -
five per mechanism class, then the class pivots. A refused scheme is
a recorded negative, not a spent idea.

## Falsifier

The class closes when every fetch surface either refused verbatim or
returned responses indistinguishable from a no-fetch control - and the
negative lines were recorded.
